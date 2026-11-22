Create database if not exists store_system_db; 
use store_system_db;

create table employee (
	eID Char(36) primary key,
    ename varchar(75) not null,
    google_sub varchar(255) unique not null,
    email varchar(50) unique not null,
    erole varchar(50),
    supervisor_eID char(36) null,
    joinDate datetime default (current_date()),
    mobile_number char(10) unique not null,
    constraint fk_supervisor
    foreign key (supervisor_eID)
    references Employee(eID)
);


Create table Customer(
	cID char(36) primary key ,
    Cname varchar(75) ,
    mobile_number char(10) unique not null
);

create table receipt(
	rID char(36) primary key ,
    totalDiscount Decimal(10, 2) default 0,
    totalPrice Decimal(10, 2) not null,
    rDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    cID char(36),
    eID char(36),
    constraint fk_employee
		foreign key (eID)
        references Employee(eID),
        
	constraint fk_customer
		foreign key (cID)
        references Customer(cID)
);

create table supplier(
	sID char(36) primary key,
    sname varchar(75),
    mobile_number char(10) unique,
    email varchar(50) unique
);

Create table category(
	category_ID char(36) primary key,
    category_name varchar(30) not null
);

Create table product(
	pID char(36) primary key,
    pName varchar(75) not null,
    price Decimal(10, 2) not null,
    quantity int not null,
    discount Decimal(10, 2),
    sID char(36),
    category_id char(36),
    constraint fk_supplier
		foreign key (sID)
        references Supplier(sID),
        
	constraint fk_category
		foreign key (category_id)
        references Category(category_id)
);

create table receipt_product(
	rID char(36),
    pID char(36),
    PRIMARY KEY (rID, pID),
    quantity_sold int not null,
    price_at_sale Decimal(10, 2) not null,
    constraint fk_receipt
		foreign key (rID)
        references Receipt(rID),
        
	constraint fk_product
		foreign key (pID)
        references Product(pID)
);

INSERT INTO employee (eID, ename, google_sub, email, erole, supervisor_eID, mobile_number)
VALUES 
('11111111-1111-1111-1111-111111111111', 'Ahmed Al-Qahtani', 'sub_ahmed_101', 'ahmed@store.com', 'Manager', NULL, '0501111111'),
('22222222-2222-2222-2222-222222222222', 'Saad Al-Otaibi', 'sub_saad_102', 'saad@store.com', 'Cashier', '11111111-1111-1111-1111-111111111111', '0502222222');

INSERT INTO customer (cID, Cname, mobile_number)
VALUES 
('33333333-3333-3333-3333-333333333333', 'Khalid Al-Dosari', '0553333333'),
('33333333-3333-3333-3333-333333333334', 'Nasser Al-Harbi', '0554444444');

INSERT INTO supplier (sID, sname, mobile_number, email)
VALUES 
('44444444-4444-4444-4444-444444444444', 'Almarai Distribution', '0565555555', 'sales@almarai-dist.com'),
('44444444-4444-4444-4444-444444444445', 'Riyadh Tech Supplies', '0566666666', 'info@riyadhtech.com');

INSERT INTO category (category_ID, category_name)
VALUES 
('55555555-5555-5555-5555-555555555555', 'Beverages'),
('55555555-5555-5555-5555-555555555556', 'Electronics');


INSERT INTO product (pID, pName, price, quantity, discount, sID, category_id)
VALUES 
('66666666-6666-6666-6666-666666666666', 'Fresh Orange Juice 1L', 12.50, 100, 1.50, '44444444-4444-4444-4444-444444444444', '55555555-5555-5555-5555-555555555555'),
('77777777-7777-7777-7777-777777777777', 'Wireless Mouse', 85.00, 40, 5.00, '44444444-4444-4444-4444-444444444445', '55555555-5555-5555-5555-555555555556');


INSERT INTO receipt (rID, totalDiscount, totalPrice, cID, eID)
VALUES 
('88888888-8888-8888-8888-888888888888', 8.00, 102.00, '33333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222222');

INSERT INTO receipt_product (rID, pID, quantity_sold, price_at_sale)
VALUES 
('88888888-8888-8888-8888-888888888888', '66666666-6666-6666-6666-666666666666', 2, 11.00),
('88888888-8888-8888-8888-888888888888', '77777777-7777-7777-7777-777777777777', 1, 80.00);


SELECT 
    p.pID, 
    p.pName, 
    p.price, 
    p.quantity, 
    p.discount, 
    c.category_name, 
    s.sname AS supplier_name
FROM product p
JOIN category c ON p.category_id = c.category_ID
JOIN supplier s ON p.sID = s.sID;

SELECT pID, pName, price, quantity
FROM product
WHERE pName LIKE '%Juice%' OR pID = '66666666-6666-6666-6666-666666666666';

SELECT 
    r.rID, 
    r.rDate, 
    c.Cname AS customer_name, 
    e.ename AS cashier_name, 
    p.pName AS product_name, 
    rp.quantity_sold, 
    rp.price_at_sale,
    r.totalPrice
FROM receipt r
JOIN customer c ON r.cID = c.cID
JOIN employee e ON r.eID = e.eID
JOIN receipt_product rp ON r.rID = rp.rID
JOIN product p ON rp.pID = p.pID
WHERE r.rID = '88888888-8888-8888-8888-888888888888';

UPDATE product
SET quantity = quantity - 2
WHERE pID = '66666666-6666-6666-6666-666666666666' AND quantity >= 2;

DELETE FROM product
WHERE pID = '77777777-7777-7777-7777-777777777777';