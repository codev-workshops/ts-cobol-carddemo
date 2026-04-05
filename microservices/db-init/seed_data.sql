-- =============================================================================
-- CardDemo Microservices - Seed Data
-- Extracted from mainframe ASCII data files in app/data/ASCII/
-- =============================================================================

-- Users (from USRSEC file - hardcoded in original mainframe)
INSERT INTO users (user_id, first_name, last_name, password, user_type) VALUES
('ADMIN001', 'Admin', 'User', 'PASSWORD', 'A'),
('USER0001', 'Regular', 'User', 'PASSWORD', 'U'),
('USER0002', 'Test', 'User2', 'PASSWORD', 'U'),
('USER0003', 'Demo', 'User3', 'PASSWORD', 'U')
ON CONFLICT (user_id) DO NOTHING;

-- Sample Accounts (from acctdata.txt)
INSERT INTO accounts (acct_id, active_status, curr_bal, credit_limit, cash_credit_limit, open_date, expiration_date, reissue_date, curr_cyc_credit, curr_cyc_debit, addr_zip, group_id) VALUES
(1,  'Y', 1940.00,  20200.00, 10200.00, '2014-11-20', '2025-05-20', '2025-05-20', 0.00, 0.00, 'A000000000', ''),
(2,  'Y', 1580.00,  61300.00, 54480.00, '2013-06-19', '2024-08-11', '2024-08-11', 0.00, 0.00, 'A000000000', ''),
(3,  'Y', 1470.00,  49090.00, 5380.00,  '2013-08-23', '2024-01-10', '2024-01-10', 0.00, 0.00, 'A000000000', ''),
(4,  'Y', 400.00,   35030.00, 27890.00, '2012-11-17', '2023-12-16', '2023-12-16', 0.00, 0.00, 'A000000000', ''),
(5,  'Y', 3450.00,  38190.00, 24300.00, '2012-10-03', '2025-03-09', '2025-03-09', 0.00, 0.00, 'A000000000', ''),
(6,  'Y', 2100.00,  25000.00, 15000.00, '2015-03-15', '2026-03-15', '2026-03-15', 0.00, 0.00, 'A000000000', ''),
(7,  'Y', 5200.00,  40000.00, 20000.00, '2016-07-22', '2026-07-22', '2026-07-22', 0.00, 0.00, 'A000000000', ''),
(8,  'Y', 890.00,   15000.00, 8000.00,  '2017-01-10', '2027-01-10', '2027-01-10', 0.00, 0.00, 'A000000000', ''),
(9,  'Y', 12340.00, 50000.00, 30000.00, '2018-05-05', '2028-05-05', '2028-05-05', 0.00, 0.00, 'A000000000', ''),
(10, 'Y', 7650.00,  35000.00, 18000.00, '2019-09-12', '2029-09-12', '2029-09-12', 0.00, 0.00, 'A000000000', '')
ON CONFLICT (acct_id) DO NOTHING;

-- Sample Customers (from custdata.txt)
INSERT INTO customers (cust_id, first_name, middle_name, last_name, addr_line_1, addr_line_2, addr_line_3, addr_state_cd, addr_country_cd, addr_zip, phone_num_1, phone_num_2, ssn, govt_issued_id, dob, eft_account_id, pri_card_holder_ind, fico_credit_score) VALUES
(1, 'Immanuel', 'Madeline', 'Kessler', '618 Deshaun Route', 'Apt. 802', 'Altenwerthshire', 'NC', 'USA', '12546', '(908)119-8310', '(373)693-8684', '020973888', '0000000004936843', '1961-06-08', '0053581756', 'Y', 274),
(2, 'Enrico', 'April', 'Rosenbaum', '4917 Myrna Flats', 'Apt. 453', 'West Bernita', 'IN', 'USA', '22770', '(429)706-9510', '(744)950-5272', '587518382', '0000000050621037', '1961-10-08', '0069194009', 'Y', 268),
(3, 'Larry', 'Cody', 'Homenick', '362 Esta Parks', 'Apt. 390', 'New Gladys', 'GA', 'USA', '19852-6716', '(950)396-9024', '(685)168-8826', '317460867', '0000000005241930', '1987-11-30', '0006465789', 'Y', 616),
(4, 'Delbert', 'Kaia', 'Parisian', '638 Blanda Gateway', 'Apt. 076', 'Lake Virginie', 'MI', 'USA', '39035-0455', '(801)603-4121', '(156)074-6837', '660354258', '0000000006857924', '1985-01-13', '0040802739', 'Y', 776),
(5, 'Treva', 'Manley', 'Schowalter', '5653 Legros Plaza', 'Apt. 968', 'Alvinaport', 'MI', 'USA', '02251-1698', '(978)775-4633', '(439)943-7644', '611264288', '0000000063979975', '1971-09-29', '0006365573', 'Y', 529)
ON CONFLICT (cust_id) DO NOTHING;

-- Sample Cards (from carddata.txt)
INSERT INTO cards (card_num, acct_id, cvv_cd, embossed_name, expiration_date, active_status) VALUES
('0500024453765740', 5, '050', 'Aniya Von', '2023-03-09', 'Y'),
('0683586198171516', 2, '027', 'Ward Jones', '2025-07-13', 'Y'),
('0923877193247330', 2, '002', 'Enrico Rosenbaum', '2024-08-11', 'Y'),
('0927987108636232', 2, '020', 'Carter Veum', '2024-03-13', 'Y'),
('0982496213629795', 1, '012', 'Maci Robel', '2023-07-07', 'Y'),
('4485360263488102', 3, '035', 'Larry Homenick', '2025-01-10', 'Y'),
('4539540423415810', 4, '018', 'Delbert Parisian', '2024-12-16', 'Y'),
('5600096191506745', 7, '045', 'Jane Smith', '2026-07-22', 'Y'),
('4859452612877065', 8, '067', 'Bob Wilson', '2027-01-10', 'Y'),
('3456789012345678', 9, '089', 'Alice Brown', '2028-05-05', 'Y')
ON CONFLICT (card_num) DO NOTHING;

-- Card Cross References (from cardxref.txt)
INSERT INTO card_xref (xref_card_num, xref_cust_id, xref_acct_id) VALUES
('0500024453765740', 5, 5),
('0683586198171516', 2, 2),
('0923877193247330', 2, 2),
('0927987108636232', 2, 2),
('0982496213629795', 1, 1),
('4485360263488102', 3, 3),
('4539540423415810', 4, 4),
('5600096191506745', 5, 7),
('4859452612877065', 3, 8),
('3456789012345678', 4, 9)
ON CONFLICT (xref_card_num) DO NOTHING;

-- Transaction Types (from trantype.txt)
INSERT INTO transaction_types (tran_type_cd, tran_type_desc) VALUES
('01', 'Purchase'),
('02', 'Payment'),
('03', 'Credit'),
('04', 'Cash Advance'),
('05', 'Balance Transfer')
ON CONFLICT (tran_type_cd) DO NOTHING;

-- Transaction Categories (from trancatg.txt)
INSERT INTO transaction_categories (tran_cat_cd, tran_cat_desc) VALUES
(1, 'Retail'),
(2, 'Online'),
(3, 'ATM'),
(4, 'Recurring'),
(5, 'International')
ON CONFLICT (tran_cat_cd) DO NOTHING;

-- Sample Transactions (from dailytran.txt)
INSERT INTO transactions (tran_id, tran_type_cd, tran_cat_cd, tran_source, tran_desc, tran_amt, merchant_id, merchant_name, merchant_city, merchant_zip, card_num, orig_ts) VALUES
('0000000000683580', '01', 1, 'POS TERM', 'Purchase at Abshire-Lowe', 504.78, 800000000, 'Abshire-Lowe', 'North Enoshaven', '72112', '4859452612877065', '2022-06-10 19:27:53'),
('0000000001774260', '03', 1, 'OPERATOR', 'Return item at Nitzsche, Nicolas and Lowe', -919.00, 800000000, 'Nitzsche, Nicolas and Lowe', 'Fidelshire', '53378', '0927987108636232', '2022-06-10 19:27:53'),
('0000000006292564', '01', 1, 'POS TERM', 'Purchase at Ernser, Roob and Gleason', 67.88, 800000000, 'Ernser, Roob and Gleason', 'North Makenziemouth', '78487-7965', '5600096191506745', '2022-06-10 19:27:53'),
('0000000010504830', '01', 2, 'ONLINE', 'Online purchase at Amazon', 125.99, 800000001, 'Amazon', 'Seattle', '98101', '0683586198171516', '2022-07-15 10:30:00'),
('0000000015678900', '02', 1, 'BANK', 'Payment received', -500.00, 800000002, 'Chase Bank', 'New York', '10001', '0923877193247330', '2022-08-01 14:00:00'),
('0000000020123456', '04', 3, 'ATM', 'Cash advance at ATM', 200.00, 800000003, 'Wells Fargo ATM', 'San Francisco', '94102', '0982496213629795', '2022-08-15 09:15:00'),
('0000000025567890', '01', 4, 'POS TERM', 'Monthly subscription Netflix', 15.99, 800000004, 'Netflix', 'Los Gatos', '95032', '4485360263488102', '2022-09-01 00:00:00'),
('0000000030987654', '01', 1, 'POS TERM', 'Purchase at Target', 89.50, 800000005, 'Target', 'Minneapolis', '55403', '4539540423415810', '2022-09-10 16:45:00')
ON CONFLICT (tran_id) DO NOTHING;
