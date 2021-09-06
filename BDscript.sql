-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 30-08-2021 a las 17:31:12
-- Versión del servidor: 10.4.20-MariaDB
-- Versión de PHP: 8.0.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `streaming_system`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `bitcoin`
--

CREATE TABLE IF NOT EXISTS `bitcoin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `bitcoin`
--

INSERT INTO `bitcoin` (`id`, `user`, `name`, `email`, `date`) VALUES
(4, 'Samantha Ramirez', 'Christian Ramirez', 'christian@gmail.com', '2021-08-19');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `client`
--

CREATE TABLE IF NOT EXISTS `client` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `phone` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `select_platform` varchar(255) NOT NULL,
  `select_payment_method` varchar(255) NOT NULL,
  `receipt` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `client`
--

INSERT INTO `client` (`id`, `user`, `name`, `phone`, `email`, `select_platform`, `select_payment_method`, `receipt`) VALUES
(10, 'Samantha Ramirez', 'Vegeta', '0416543213', 'vegeta@gmail.com', '29', '20', 'paypal.png'),
(14, 'Samantha Ramirez', 'Chuty', '04129578692', 'chuty@gmail.com', '31', '19', 'paypal.png');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pago_movil`
--

CREATE TABLE IF NOT EXISTS `pago_movil` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `ci` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `pago_movil`
--

INSERT INTO `pago_movil` (`id`, `user`, `email`, `ci`) VALUES
(1, 'Samantha Ramirez', 'samantha.p.ramirez.y@gmail.com', 'ID.jpg');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `payment_method`
--

CREATE TABLE IF NOT EXISTS `payment_method` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `payment_platform_name` varchar(255) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `required_fields` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `payment_method`
--

INSERT INTO `payment_method` (`id`, `user`, `payment_platform_name`, `file_name`, `required_fields`) VALUES
(19, 'Samantha Ramirez', 'Bitcoin', 'disney.jpg', 'name, email, date'),
(20, 'Samantha Ramirez', 'Pago_movil', 'amazon.png', 'email, ci');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `platform`
--

CREATE TABLE IF NOT EXISTS `platform` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `screen_amount` int(11) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `duration` varchar(255) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `platform`
--

INSERT INTO `platform` (`id`, `user`, `name`, `url`, `screen_amount`, `start_date`, `end_date`, `duration`, `file_name`) VALUES
(5, 'Samantha Ramirez', 'Amazon Prime', 'https://es.scribd.com/document/144965474/La-economia-del-gobierno-de-Luis-Herrera-Campins', 4, '2021-08-01', '2021-10-31', '3 months', 'amazon.png'),
(18, 'Samantha Ramirez', 'Netflix', 'https://www.netflix.com', 4, '2021-08-01', '2021-08-31', '1 months', 'netflix.jpg'),
(20, 'Samantha Ramirez', 'HBO max', 'https://www.hbomax.com/', 5, '2021-08-25', '2021-10-25', '2 months', 'hbo.jpg');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `screen`
--

CREATE TABLE IF NOT EXISTS `screen` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `account_id` int(11) NOT NULL,
  `number` int(11) NOT NULL,
  `platform` varchar(255) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `duration` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `client` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `screen`
--

INSERT INTO `screen` (`id`, `account_id`, `number`, `platform`, `start_date`, `end_date`, `duration`, `url`, `email`, `password`, `client`) VALUES
(29, 29, 1, 'Netflix', '2021-08-01', '2021-08-31', '1 months', 'https://www.netflix.com', 'cuenta@gmail.com', 'cuenta', NULL),
(30, 29, 2, 'Netflix', '2021-08-01', '2021-08-31', '1 months', 'https://www.netflix.com', 'cuenta@gmail.com', 'cuenta', NULL),
(31, 29, 3, 'Netflix', '2021-08-01', '2021-08-31', '1 months', 'https://www.netflix.com', 'cuenta@gmail.com', 'cuenta', NULL),
(32, 29, 4, 'Netflix', '2021-08-01', '2021-08-31', '1 months', 'https://www.netflix.com', 'cuenta@gmail.com', 'cuenta', NULL),
(34, 31, 1, 'Amazon Prime', '2021-08-01', '2021-10-31', '3 months', 'https://es.scribd.com/document/144965474/La-economia-del-gobierno-de-Luis-Herrera-Campins', 'prueba2@gmail.com', 'prueba2', 14),
(35, 31, 2, 'Amazon Prime', '2021-08-01', '2021-10-31', '3 months', 'https://es.scribd.com/document/144965474/La-economia-del-gobierno-de-Luis-Herrera-Campins', 'prueba2@gmail.com', 'prueba2', 14),
(36, 31, 3, 'Amazon Prime', '2021-08-01', '2021-10-31', '3 months', 'https://es.scribd.com/document/144965474/La-economia-del-gobierno-de-Luis-Herrera-Campins', 'prueba2@gmail.com', 'prueba2', 14),
(37, 31, 4, 'Amazon Prime', '2021-08-01', '2021-10-31', '3 months', 'https://es.scribd.com/document/144965474/La-economia-del-gobierno-de-Luis-Herrera-Campins', 'prueba2@gmail.com', 'prueba2', 14);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `streaming_account`
--

CREATE TABLE IF NOT EXISTS `streaming_account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `select_platform` int(11) NOT NULL,
  `select_supplier` int(11) NOT NULL,
  `date` date NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `last_screens` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `streaming_account`
--

INSERT INTO `streaming_account` (`id`, `user`, `select_platform`, `select_supplier`, `date`, `email`, `password`, `last_screens`) VALUES
(29, 'Samantha Ramirez', 18, 10, '2021-08-25', 'cuenta@gmail.com', 'cuenta', 4),
(31, 'Samantha Ramirez', 5, 9, '2021-08-25', 'prueba2@gmail.com', 'prueba2', 3);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `supplier`
--

CREATE TABLE IF NOT EXISTS `supplier` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `platform_that_supplies` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(255) NOT NULL,
  `local_phone` varchar(255) NOT NULL,
  `telegram` varchar(255) NOT NULL,
  `country` varchar(255) NOT NULL,
  `paypal` varchar(255) NOT NULL,
  `pago_movil` varchar(255) NOT NULL,
  `bank` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `supplier`
--

INSERT INTO `supplier` (`id`, `user`, `name`, `platform_that_supplies`, `email`, `phone`, `local_phone`, `telegram`, `country`, `paypal`, `pago_movil`, `bank`) VALUES
(9, 'Samantha Ramirez', 'Maria Travieso', 18, 'maria@gmail.com', '04123454321', '02123454387', 'MariaT', 'Venezuela', 'maria@gmail.com', '04123453345, 31309987, Banesco', 'Banesco'),
(10, 'Samantha Ramirez', 'Tom Hiddleston', 20, 'tomwhiddleston@gmail.com', '04123456778', '02123456778', 'TomWHiddleston', 'Inglaterra', 'tom@gmail.com', '04123453345, 31309987, Mercantil', 'Mercantil');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `user`
--

CREATE TABLE IF NOT EXISTS `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_type` varchar(255) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `phone` varchar(100) NOT NULL,
  `ci` varchar(100) NOT NULL,
  `gender` varchar(255) NOT NULL,
  `facebook` varchar(100) NOT NULL,
  `instagram` varchar(100) NOT NULL,
  `social_media` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `user`
--

INSERT INTO `user` (`id`, `user_type`, `parent_id`, `username`, `email`, `password`, `phone`, `ci`, `gender`, `facebook`, `instagram`, `social_media`) VALUES
(7, 'admin', NULL, 'Samantha Ramirez', 'samantha.p.ramirez.y@gmail.com', 'hola', '04129578692', '31307714', 'Woman', 'Samantha R', 'SamR', 'WhatsApp, Telegram'),
(8, 'seller', 7, 'Maria Travieso', 'maria@gmail.com', 'maria', '04123456789', '31321234', 'Woman', 'MariaT', 'MariaT', 'Telegram'),
(10, 'seller', 7, 'Christian Ramirez', 'christian@gmail.com', 'hello', '041234567', '31307715', 'Man', 'Christian', 'ChrisR', 'WhatsApp'),
(11, 'client', 7, 'Michelle Torres', 'mich@gmail.com', 'mich', '04123454321', '31307713', 'Woman', 'michT', 'michtorres', 'WhatsApp, Messenger, Telegram');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
