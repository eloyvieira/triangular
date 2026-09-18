-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Sep 18, 2026 at 02:22 AM
-- Server version: 10.6.23-MariaDB-0ubuntu0.22.04.1
-- PHP Version: 8.1.34

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `triangular`
--

-- --------------------------------------------------------

--
-- Table structure for table `balances_history`
--

CREATE TABLE `balances_history` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `robot` bigint(20) UNSIGNED NOT NULL,
  `version` varchar(100) NOT NULL,
  `type` varchar(20) NOT NULL DEFAULT 'USDT',
  `balance` decimal(36,18) NOT NULL,
  `date_creation` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `balances_history`
--

INSERT INTO `balances_history` (`id`, `robot`, `version`, `type`, `balance`, `date_creation`) VALUES
(1, 1, 'bot_binance_v20', 'USDT', 100.000000000000000000, '2026-09-18 01:19:36');

-- --------------------------------------------------------

--
-- Table structure for table `binance`
--

CREATE TABLE `binance` (
  `id_symbol` varchar(30) NOT NULL,
  `symbol` varchar(40) NOT NULL,
  `min_decimal` tinyint(3) UNSIGNED NOT NULL DEFAULT 8,
  `min_amount` decimal(36,18) NOT NULL DEFAULT 0.000000000000000000,
  `dec_precision` tinyint(3) UNSIGNED NOT NULL DEFAULT 8,
  `min_precision` decimal(36,18) NOT NULL DEFAULT 0.000000010000000000,
  `quote` varchar(20) NOT NULL,
  `spread` decimal(18,8) NOT NULL DEFAULT 0.00000000,
  `spread_ask` decimal(18,8) NOT NULL DEFAULT 0.00000000,
  `up` decimal(18,8) NOT NULL DEFAULT 0.00000000,
  `down` decimal(18,8) NOT NULL DEFAULT 0.00000000,
  `status` tinyint(1) NOT NULL DEFAULT 1,
  `date_creation` datetime NOT NULL DEFAULT current_timestamp(),
  `date_update` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `binance`
--

INSERT INTO `binance` (`id_symbol`, `symbol`, `min_decimal`, `min_amount`, `dec_precision`, `min_precision`, `quote`, `spread`, `spread_ask`, `up`, `down`, `status`, `date_creation`, `date_update`) VALUES
('ADABTC', 'ADA/BTC', 1, 0.100000000000000000, 8, 0.000000010000000000, 'BTC', 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1, '2026-09-18 01:53:58', NULL),
('ADAUSDT', 'ADA/USDT', 1, 0.100000000000000000, 4, 0.000100000000000000, 'USDT', 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1, '2026-09-18 01:53:58', NULL),
('ARBBTC', 'ARB/BTC', 1, 0.100000000000000000, 8, 0.000000010000000000, 'BTC', 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1, '2026-09-18 01:53:58', NULL),
('ARBUSDT', 'ARB/USDT', 1, 0.100000000000000000, 4, 0.000100000000000000, 'USDT', 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1, '2026-09-18 01:53:58', NULL),
('BTCUSDT', 'BTC/USDT', 5, 0.000010000000000000, 2, 0.010000000000000000, 'USDT', 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1, '2026-09-17 18:28:05', '2026-09-18 01:53:58'),
('DASHBTC', 'DASH/BTC', 3, 0.001000000000000000, 7, 0.000000100000000000, 'BTC', 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1, '2026-09-18 01:53:58', NULL),
('DASHUSDT', 'DASH/USDT', 3, 0.001000000000000000, 2, 0.010000000000000000, 'USDT', 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1, '2026-09-18 01:53:58', NULL),
('DOGEBTC', 'DOGE/BTC', 0, 1.000000000000000000, 8, 0.000000010000000000, 'BTC', 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1, '2026-09-18 01:53:58', NULL),
('DOGEUSDT', 'DOGE/USDT', 0, 1.000000000000000000, 5, 0.000010000000000000, 'USDT', 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1, '2026-09-18 01:53:58', NULL),
('ETHBTC', 'ETH/BTC', 4, 0.000100000000000000, 5, 0.000010000000000000, 'BTC', 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1, '2026-09-18 01:27:59', '2026-09-18 01:53:58'),
('ETHUSDT', 'ETH/USDT', 4, 0.000100000000000000, 2, 0.010000000000000000, 'USDT', 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1, '2026-09-18 01:27:59', '2026-09-18 01:53:58'),
('XRPBTC', 'XRP/BTC', 1, 0.100000000000000000, 8, 0.000000010000000000, 'BTC', 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1, '2026-09-18 01:53:58', NULL),
('XRPUSDT', 'XRP/USDT', 1, 0.100000000000000000, 4, 0.000100000000000000, 'USDT', 0.00000000, 0.00000000, 0.00000000, 0.00000000, 1, '2026-09-18 01:53:58', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `binance_market`
--

CREATE TABLE `binance_market` (
  `id_symbol` varchar(30) NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 1,
  `date_creation` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `binance_market`
--

INSERT INTO `binance_market` (`id_symbol`, `status`, `date_creation`) VALUES
('ADABTC', 1, '2026-09-18 01:41:46'),
('ADAUSDT', 1, '2026-09-18 01:41:46'),
('ARBBTC', 1, '2026-09-18 01:45:48'),
('ARBUSDT', 1, '2026-09-18 01:45:48'),
('BTCUSDT', 1, '2026-09-17 18:28:05'),
('DASHBTC', 1, '2026-09-18 01:45:48'),
('DASHUSDT', 1, '2026-09-18 01:45:48'),
('DOGEBTC', 1, '2026-09-18 01:45:48'),
('DOGEUSDT', 1, '2026-09-18 01:45:48'),
('ETHBTC', 1, '2026-09-18 01:18:10'),
('ETHUSDT', 1, '2026-09-18 01:18:10'),
('XRPBTC', 1, '2026-09-18 01:41:46'),
('XRPUSDT', 1, '2026-09-18 01:41:46');

-- --------------------------------------------------------

--
-- Table structure for table `binance_orders`
--

CREATE TABLE `binance_orders` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `script` varchar(100) DEFAULT NULL,
  `data` longtext DEFAULT NULL,
  `market1` varchar(30) DEFAULT NULL,
  `quote` varchar(20) DEFAULT NULL,
  `market2` varchar(30) DEFAULT NULL,
  `market3` varchar(30) DEFAULT NULL,
  `status` tinyint(4) NOT NULL DEFAULT 0,
  `date_creation` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `lockunlock`
--

CREATE TABLE `lockunlock` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `script` varchar(100) NOT NULL,
  `data` longtext DEFAULT NULL,
  `date_creation` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `log`
--

CREATE TABLE `log` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `robot` bigint(20) UNSIGNED NOT NULL,
  `version` varchar(100) NOT NULL,
  `data` longtext DEFAULT NULL,
  `date_creation` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `log`
--

INSERT INTO `log` (`id`, `robot`, `version`, `data`, `date_creation`) VALUES
(1, 1, 'bot_slave15', 'restart', '2026-09-18 01:16:54'),
(2, 1, 'bot_slave15', 'restart', '2026-09-18 01:17:06'),
(3, 1, 'bot_slave15', 'restart', '2026-09-18 01:18:14');

-- --------------------------------------------------------

--
-- Table structure for table `opportunities`
--

CREATE TABLE `opportunities` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `side` varchar(20) NOT NULL,
  `market1` varchar(30) NOT NULL,
  `market2` varchar(30) NOT NULL,
  `market3` varchar(30) NOT NULL,
  `price1` decimal(36,18) NOT NULL,
  `price2` decimal(36,18) NOT NULL,
  `price3` decimal(36,18) NOT NULL,
  `amount1_in` decimal(36,18) NOT NULL,
  `amount1_out` decimal(36,18) NOT NULL,
  `perc1` decimal(18,8) NOT NULL,
  `amount2_in` decimal(36,18) NOT NULL,
  `amount2_out` decimal(36,18) NOT NULL,
  `perc2` decimal(18,8) NOT NULL,
  `date_creation` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `robot`
--

CREATE TABLE `robot` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `api_key` varchar(255) NOT NULL,
  `api_secret` varchar(255) NOT NULL,
  `api_uid` varchar(255) DEFAULT NULL,
  `private_ip` varchar(45) NOT NULL,
  `version` varchar(100) NOT NULL,
  `exchanges` varchar(50) NOT NULL DEFAULT 'binance',
  `status` tinyint(1) NOT NULL DEFAULT 1,
  `date_creation` datetime NOT NULL DEFAULT current_timestamp(),
  `date_update` datetime DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `robot`
--

INSERT INTO `robot` (`id`, `api_key`, `api_secret`, `api_uid`, `private_ip`, `version`, `exchanges`, `status`, `date_creation`, `date_update`) VALUES
(1, 'apikey', 'apisecret', '', '127.0.0.1', 'bot_binance_v20', 'binance', 1, '2026-09-17 19:39:45', '2026-09-18 01:10:31');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `balances_history`
--
ALTER TABLE `balances_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_balance_last` (`robot`,`version`,`type`,`id`);

--
-- Indexes for table `binance`
--
ALTER TABLE `binance`
  ADD PRIMARY KEY (`id_symbol`),
  ADD UNIQUE KEY `uk_binance_symbol` (`symbol`),
  ADD KEY `idx_binance_quote_status` (`quote`,`status`);

--
-- Indexes for table `binance_market`
--
ALTER TABLE `binance_market`
  ADD PRIMARY KEY (`id_symbol`),
  ADD KEY `idx_binance_market_status` (`status`);

--
-- Indexes for table `binance_orders`
--
ALTER TABLE `binance_orders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_triangular_orders_status` (`status`,`id`),
  ADD KEY `idx_triangular_orders_script` (`script`,`date_creation`);

--
-- Indexes for table `lockunlock`
--
ALTER TABLE `lockunlock`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_lockunlock_script` (`script`),
  ADD KEY `idx_lockunlock_date` (`date_creation`);

--
-- Indexes for table `log`
--
ALTER TABLE `log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_log_robot_date` (`robot`,`date_creation`),
  ADD KEY `idx_log_version_date` (`version`,`date_creation`);

--
-- Indexes for table `opportunities`
--
ALTER TABLE `opportunities`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_opportunities_date` (`date_creation`),
  ADD KEY `idx_opportunities_route` (`side`,`market1`,`market2`,`market3`);

--
-- Indexes for table `robot`
--
ALTER TABLE `robot`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_robot_lookup` (`private_ip`,`version`,`exchanges`,`status`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `balances_history`
--
ALTER TABLE `balances_history`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `binance_orders`
--
ALTER TABLE `binance_orders`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `lockunlock`
--
ALTER TABLE `lockunlock`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `log`
--
ALTER TABLE `log`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `opportunities`
--
ALTER TABLE `opportunities`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `robot`
--
ALTER TABLE `robot`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
