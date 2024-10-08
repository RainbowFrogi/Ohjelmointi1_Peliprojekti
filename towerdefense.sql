-- --------------------------------------------------------
-- Verkkotietokone:              127.0.0.1
-- Palvelinversio:               11.5.2-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Versio:              12.6.0.6765
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP DATABASE IF EXISTS towerdefense;

CREATE DATABASE IF NOT EXISTS towerdefense /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
USE towerdefense;

/*before using the script, create a user with the name of 'TDuser'@'localhost'and password of '1234'*/
-- CREATE USER 'TDuser'@'localhost' IDENTIFIED BY '1234';
GRANT SELECT, INSERT, UPDATE, DELETE ON towerdefense.* TO 'TDuser'@'localhost';

FLUSH PRIVILEGES;

-- Dumping structure for taulu towerdefense.enemies
CREATE TABLE IF NOT EXISTS `enemies` (
  `id` int(11) NOT NULL,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `speed` float NOT NULL DEFAULT 0,
  `damage` int(11) NOT NULL DEFAULT 0,
  `health` int(11) NOT NULL DEFAULT 0,
  `regen` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Dumping data for table towerdefense.enemies: ~4 rows (suunnilleen)
INSERT INTO `enemies` (`id`, `name`, `speed`, `damage`, `health`, `regen`) VALUES
	(1, 'soldier', 1.3, 1, 100, 0),
	(2, 'heavy', 0.8, 2, 150, 0),
	(3, 'rogue', 2, 1, 50, 0),
	(4, 'elite', 1.5, 3, 300, 1);

-- Dumping structure for taulu towerdefense.turrets
CREATE TABLE IF NOT EXISTS `turrets` (
  `id` int(11) NOT NULL,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `cooldown` float NOT NULL DEFAULT 0,
  `turret_range` float NOT NULL DEFAULT 0,
  `damage` int(11) NOT NULL DEFAULT 0,
  `cost` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Dumping data for table towerdefense.turrets: ~5 rows (suunnilleen)
INSERT INTO `turrets` (`id`, `name`, `cooldown`, `turret_range`, `damage`, `cost`) VALUES
	(1, 'mk5', 400, 90, 35, 50),
	(2, 'mk10', 400, 115, 35, 200),
	(3, 'mk15', 300, 150, 35, 300),
	(4, 'mk20', 300, 175, 35, 500),
	(5, 'laser', 0, 175, 1, 400);

-- Dumping structure for taulu towerdefense.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL,
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `highest_wave` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Dumping data for table towerdefense.users: ~0 rows (suunnilleen)

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
