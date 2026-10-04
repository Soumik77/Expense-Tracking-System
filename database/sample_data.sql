-- Synthetic examples only. Run once in an empty demo database.
USE expense_manager;

INSERT INTO expenses (expense_date, amount, category, notes) VALUES
('2026-08-02', 25.50, 'Food', 'Sample groceries'),
('2026-08-02', 12.00, 'Other', 'Sample transport'),
('2026-08-15', 45.00, 'Shopping', 'Sample purchase'),
('2026-09-01', 500.00, 'Rent', 'Sample rent'),
('2026-09-03', 30.25, 'Food', 'Sample groceries'),
('2026-09-03', 15.00, 'Entertainment', 'Sample ticket');
