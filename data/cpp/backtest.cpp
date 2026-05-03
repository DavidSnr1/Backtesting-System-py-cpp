// backtest.cpp
// C++ backtest engine mirroring Python portfolio.py + backtest.py
// Usage: backtest.exe <csv_file> <strategy> [params...]
// Strategies: mov_avg, buy_and_hold, rsi, dual_ma, bollinger
 
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <numeric>
#include <algorithm>
#include <cmath>
#include <chrono>
#include <sstream>
 
// ========================================
// RUNTIME CONFIG (mirrors config.py)
// ========================================

struct RuntimeConfig {
    double transaction_cost = 0.001;
    double initial_capital  = 10000000.0;
    double fraction_position = 0.1;

    double trading_days  = 365.0;
    double hours_per_day = 24.0;
    double interval_hours = 1.0;

    int mov_avg_window = 20;
    double mov_avg_threshold_buy = 0.01;
    double mov_avg_threshold_sell = 0.01;

    int rsi_window = 14;
    double rsi_oversold = 30.0;
    double rsi_overbought = 70.0;

    int dual_ma_window_short = 10;
    int dual_ma_window_long = 50;

    int bollinger_window = 20;
    double bollinger_num_std = 2.0;
};
 
// ========================================
// PORTFOLIO (mirrors portfolio.py)
// ========================================
 
struct Trade {
    double buy_price;
    double sell_price;
};
 
struct Portfolio {
    double cash;
    int    shares;
    double initial_capital;
    double fees;
    double transaction_cost;
 
    // buy_history and sell_history for win rate calculation
    std::vector<double> buy_history;
    std::vector<double> sell_history;
 
        Portfolio(double capital, double txn_cost)
        : cash(capital), shares(0),
                    initial_capital(capital), fees(0.0), transaction_cost(txn_cost) {}
 
    bool check_buy(int size, double price) {
        double cost = size * price;
        double fee  = cost * transaction_cost;
        return cash >= (cost + fee);
    }
 
    bool buy(int size, double price) {
        double cost = size * price;
        double fee  = cost * transaction_cost;
        cost += fee;
        if (check_buy(size, price)) {
            cash   -= cost;
            shares += size;
            fees   += fee;
            buy_history.push_back(price);
            return true;
        }
        return false;
    }
 
    bool check_sell(int size) {
        return shares >= size;
    }
 
    bool sell(int size, double price) {
        double revenue = size * price;
        double fee     = revenue * transaction_cost;
        revenue -= fee;
        if (check_sell(size)) {
            cash   += revenue;
            shares -= size;
            fees   += fee;
            sell_history.push_back(price);
            return true;
        }
        return false;
    }
 
    double total(double current_price) {
        return cash + shares * current_price;
    }
 
    double profit_loss(double current_price) {
        return total(current_price) - initial_capital;
    }
 
    double roi(double current_price) {
        return (profit_loss(current_price) / initial_capital) * 100.0;
    }
 
    // mirrors portfolio.max_dd()
    double max_dd(const std::vector<double>& total_history) {
        if (total_history.empty()) return 0.0;
        double peak        = total_history[0];
        double max_drawdown = 0.0;
        for (double val : total_history) {
            if (val > peak) peak = val;
            double dd = (peak - val) / peak;
            if (dd > max_drawdown) max_drawdown = dd;
        }
        return max_drawdown * 100.0;
    }
 
    // mirrors portfolio.sharpe_ratio()
    double sharpe_ratio(const std::vector<double>& total_history,
                        double trading_days,
                        double hours_per_day,
                        double interval_hours) {
        if (total_history.size() < 2) return 0.0;
 
        // pct_change
        std::vector<double> returns;
        for (size_t i = 1; i < total_history.size(); i++) {
            if (total_history[i - 1] != 0.0)
                returns.push_back(
                    (total_history[i] - total_history[i - 1])
                    / total_history[i - 1]);
        }
 
        if (returns.empty()) return 0.0;
 
        double mean = std::accumulate(returns.begin(), returns.end(), 0.0)
                      / returns.size();
 
        double variance = 0.0;
        for (double r : returns)
            variance += (r - mean) * (r - mean);
        variance /= returns.size();
        double std_dev = std::sqrt(variance);
 
        if (std_dev == 0.0) return 0.0;
 
        // Annualization identical to Python
        if (interval_hours <= 0.0) return 0.0;
        double periods_per_year = trading_days * hours_per_day / interval_hours;
        double annualization    = std::sqrt(periods_per_year);
 
        return (mean / std_dev) * annualization;
    }
 
    // mirrors portfolio.calculate_win_rate()
    std::pair<double, int> calculate_win_rate() {
        size_t n = std::min(buy_history.size(), sell_history.size());
        if (n == 0) return {0.0, 0};
 
        int wins = 0;
        for (size_t i = 0; i < n; i++) {
            if (sell_history[i] > buy_history[i]) wins++;
        }
        double win_rate = (double)wins / n * 100.0;
        return {win_rate, (int)n};
    }
};
 
// ========================================
// DATA LOADING
// ========================================
 
std::vector<double> load_prices(const std::string& filename) {
    std::vector<double> prices;
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: cannot open " << filename << std::endl;
        return prices;
    }
 
    std::string line;
    std::getline(file, line); // Skip CSV header
 
    while (std::getline(file, line)) {
        size_t comma = line.find(',');
        if (comma != std::string::npos) {
            try {
                prices.push_back(std::stod(line.substr(comma + 1)));
            } catch (...) {}
        }
    }
    return prices;
}
 
// ========================================
// STRATEGIES (mirrors strategy.py)
// ========================================
 
// mirrors mov_avg_strat.signal()
std::string mov_avg_signal(const std::vector<double>& charts,
                            int idx, int window,
                            double threshold_buy, double threshold_sell) {
    if (idx < window) return "hold";
 
    double sum = 0.0;
    for (int i = idx - window; i < idx; i++) sum += charts[i];
    double avg           = sum / window;
    double current_price = charts[idx];
 
    if (current_price > avg * (1.0 + threshold_buy))  return "buy";
    if (current_price < avg * (1.0 - threshold_sell)) return "sell";
    return "hold";
}
 
// mirrors buy_and_hold_strat.signal()
std::string buy_and_hold_signal(int idx) {
    return (idx == 0) ? "buy" : "hold";
}
 
// mirrors rsi_strat.signal()
std::string rsi_signal(const std::vector<double>& charts,
                        int idx, int window,
                        double oversold, double overbought) {
    if (idx < window) return "hold";
 
    double gains  = 0.0;
    double losses = 0.0;
    for (int i = idx - window; i < idx; i++) {
        double delta = charts[i + 1] - charts[i];
        if (delta > 0) gains  += delta;
        else           losses -= delta;
    }
 
    double rsi;
    if (losses == 0.0) {
        rsi = 100.0;
    } else {
        double rs = gains / losses;
        rsi = 100.0 - (100.0 / (1.0 + rs));
    }
 
    if (rsi < oversold)   return "buy";
    if (rsi > overbought) return "sell";
    return "hold";
}
 
// mirrors dual_ma_strat.signal()
std::string dual_ma_signal(const std::vector<double>& charts,
                            int idx, int window_short, int window_long) {
    if (idx < window_long) return "hold";
 
    double short_sum = 0.0;
    for (int i = idx - window_short; i < idx; i++) short_sum += charts[i];
    double short_avg = short_sum / window_short;
 
    double long_sum = 0.0;
    for (int i = idx - window_long; i < idx; i++) long_sum += charts[i];
    double long_avg = long_sum / window_long;
 
    if (short_avg > long_avg) return "buy";
    if (short_avg < long_avg) return "sell";
    return "hold";
}
 
// mirrors bollinger_strat.signal()
std::string bollinger_signal(const std::vector<double>& charts,
                              int idx, int window, double num_std) {
    if (idx < window) return "hold";
 
    double sum = 0.0;
    for (int i = idx - window; i < idx; i++) sum += charts[i];
    double avg = sum / window;
 
    double variance = 0.0;
    for (int i = idx - window; i < idx; i++)
        variance += (charts[i] - avg) * (charts[i] - avg);
    double std_dev = std::sqrt(variance / window);
 
    double upper_band    = avg + num_std * std_dev;
    double lower_band    = avg - num_std * std_dev;
    double current_price = charts[idx];
 
    if (current_price > upper_band) return "sell";
    if (current_price < lower_band) return "buy";
    return "hold";
}
 
// ========================================
// BACKTEST ENGINE (mirrors backtest.run_backtest())
// ========================================
 
struct BacktestResult {
    double final_value;
    double roi;
    double profit_loss;
    double max_dd;
    double sharpe;
    double win_rate;
    double total_fees;
    int    total_trades;
    double runtime_ms;
    std::string strategy_name;
};
 
BacktestResult run_backtest(const std::vector<double>& charts,
                             const std::string& strategy_name,
                             const RuntimeConfig& cfg) {
    auto start = std::chrono::high_resolution_clock::now();
 
    Portfolio p(cfg.initial_capital, cfg.transaction_cost);
    std::vector<double> total_history;
    total_history.reserve(charts.size());
 
    for (int tick = 0; tick < (int)charts.size(); tick++) {
        double price = charts[tick];
        std::string signal;
 
        // Strategy dispatch mirrors backtest.run_backtest()
        if (strategy_name == "mov_avg") {
            signal = mov_avg_signal(
                charts,
                tick,
                cfg.mov_avg_window,
                cfg.mov_avg_threshold_buy,
                cfg.mov_avg_threshold_sell
            );
        } else if (strategy_name == "buy_and_hold") {
            signal = buy_and_hold_signal(tick);
        } else if (strategy_name == "rsi") {
            signal = rsi_signal(
                charts,
                tick,
                cfg.rsi_window,
                cfg.rsi_oversold,
                cfg.rsi_overbought
            );
        } else if (strategy_name == "dual_ma") {
            signal = dual_ma_signal(
                charts,
                tick,
                cfg.dual_ma_window_short,
                cfg.dual_ma_window_long
            );
        } else if (strategy_name == "bollinger") {
            signal = bollinger_signal(
                charts,
                tick,
                cfg.bollinger_window,
                cfg.bollinger_num_std
            );
        } else {
            signal = "hold";
        }
 
        if (signal == "buy" && p.cash > 0) {
            int size = (int)(p.cash * cfg.fraction_position / price);
            if (size > 0) p.buy(size, price);
        } else if (signal == "sell" && p.shares > 0) {
            p.sell(p.shares, price);
        }
 
        total_history.push_back(p.total(price));
    }
 
    auto end = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double, std::milli>(end - start).count();
 
    auto [win_rate, total_trades] = p.calculate_win_rate();
 
    double last_price = charts.back();
    return {
        total_history.back(),
        p.roi(last_price),
        p.profit_loss(last_price),
        p.max_dd(total_history),
        p.sharpe_ratio(total_history, cfg.trading_days, cfg.hours_per_day, cfg.interval_hours),
        win_rate,
        p.fees,
        total_trades,
        ms,
        strategy_name
    };
}
 
// ========================================
// MAIN
// ========================================
 
int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: backtest.exe <csv_file> <strategy>" << std::endl;
        std::cerr << "Strategies: mov_avg | buy_and_hold | rsi | dual_ma | bollinger | all" << std::endl;
        return 1;
    }
 
    std::string csv_file      = argv[1];
    std::string strategy_name = argv[2];

    RuntimeConfig cfg;
    // Optional overrides from Python config:
    // 3: initial_capital, 4: fraction_position, 5: transaction_cost
    // 6: trading_days, 7: hours_per_day, 8: interval_hours
    // 9: mov_avg_window, 10: mov_avg_threshold_buy, 11: mov_avg_threshold_sell
    // 12: rsi_window, 13: rsi_oversold, 14: rsi_overbought
    // 15: dual_ma_window_short, 16: dual_ma_window_long
    // 17: bollinger_window, 18: bollinger_num_std
    try {
        if (argc > 3)  cfg.initial_capital = std::stod(argv[3]);
        if (argc > 4)  cfg.fraction_position = std::stod(argv[4]);
        if (argc > 5)  cfg.transaction_cost = std::stod(argv[5]);
        if (argc > 6)  cfg.trading_days = std::stod(argv[6]);
        if (argc > 7)  cfg.hours_per_day = std::stod(argv[7]);
        if (argc > 8)  cfg.interval_hours = std::stod(argv[8]);

        if (argc > 9)  cfg.mov_avg_window = std::stoi(argv[9]);
        if (argc > 10) cfg.mov_avg_threshold_buy = std::stod(argv[10]);
        if (argc > 11) cfg.mov_avg_threshold_sell = std::stod(argv[11]);

        if (argc > 12) cfg.rsi_window = std::stoi(argv[12]);
        if (argc > 13) cfg.rsi_oversold = std::stod(argv[13]);
        if (argc > 14) cfg.rsi_overbought = std::stod(argv[14]);

        if (argc > 15) cfg.dual_ma_window_short = std::stoi(argv[15]);
        if (argc > 16) cfg.dual_ma_window_long = std::stoi(argv[16]);

        if (argc > 17) cfg.bollinger_window = std::stoi(argv[17]);
        if (argc > 18) cfg.bollinger_num_std = std::stod(argv[18]);
    } catch (const std::exception& e) {
        std::cerr << "Error parsing config args: " << e.what() << std::endl;
        return 1;
    }
 
    std::vector<double> prices = load_prices(csv_file);
    if (prices.empty()) {
        std::cerr << "Error: no prices loaded from " << csv_file << std::endl;
        return 1;
    }
 
    std::vector<std::string> strategies;
    if (strategy_name == "all") {
        strategies = {"mov_avg", "buy_and_hold", "rsi", "dual_ma", "bollinger"};
    } else {
        strategies = {strategy_name};
    }
 
    // Output results for each strategy
    // Format: key:value parsed by Python
    for (const auto& strat : strategies) {
        BacktestResult r = run_backtest(prices, strat, cfg);
 
        std::cout << "strategy:"      << r.strategy_name  << std::endl;
        std::cout << "final_value:"   << r.final_value     << std::endl;
        std::cout << "roi:"           << r.roi             << std::endl;
        std::cout << "profit_loss:"   << r.profit_loss     << std::endl;
        std::cout << "max_dd:"        << r.max_dd          << std::endl;
        std::cout << "sharpe:"        << r.sharpe          << std::endl;
        std::cout << "win_rate:"      << r.win_rate        << std::endl;
        std::cout << "total_fees:"    << r.total_fees      << std::endl;
        std::cout << "total_trades:"  << r.total_trades    << std::endl;
        std::cout << "runtime_ms:"    << r.runtime_ms      << std::endl;
        std::cout << "---" << std::endl; // Separator between strategies
    }
 
    return 0;
}