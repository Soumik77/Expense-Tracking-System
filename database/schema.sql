CREATE DATABASE IF NOT EXISTS expense_manager
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE expense_manager;

CREATE TABLE IF NOT EXISTS expenses (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    expense_date DATE NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    notes VARCHAR(500) NOT NULL DEFAULT '',
    PRIMARY KEY (id),
    INDEX idx_expenses_date (expense_date),
    CONSTRAINT chk_expenses_positive_amount CHECK (amount > 0)
) ENGINE=InnoDB;
