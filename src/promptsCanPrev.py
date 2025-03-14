COMPRESSED_SCHEMA = """### **Sales Schema Summary**

#### **1. `sales_report` (Sales Data)**
- **Purpose:** Tracks **sales transactions** with order, product, account, pricing, tax, and shipment details.
- **Keys:** `order_id`, `product_sku`, `account_id`, `invoice`, `promotion_id`, `order_date`, `ship_date`
- **Metrics:** `price`, `quantity`, `cogs`, `line_amount`, `line_tax`
- **Use Case:** Sales insights, invoices, promotions, product transactions.

#### **2. `orders` (Order Details)**
- **Purpose:** Stores **order information**, payment, discounts, status, and fulfillment.
- **Keys:** `order_id`, `account_id`, `invoice_number`, `order_type_id`, `order_status_id`
- **Metrics:** `subtotal_amount`, `shipping_amount`, `tax_amount`, `total_amount`, `paid_amount`
- **Use Case:** Order processing, payments, order statuses, invoices.

#### **3. `accounts` (Customer Data)**
- **Purpose:** Holds **customer profiles** with contact, billing, and payment preferences.
- **Keys:** `account_id`, `name`, `email`, `account_type_id`, `pay_term_id`
- **Use Case:** Customer details, credit terms, account statuses.

#### **4. `products` (Product Catalog)**
- **Purpose:** Stores **product inventory, pricing, branding, and stock**.
- **Keys:** `id`, `sku`, `name`, `brand_id`
- **Metrics:** `msrp`, `cogs`, `available_qty`, `inventory_qty`, `reserved_qty`
- **Use Case:** Product details, stock levels, pricing.

#### **5. `promotions` (Discounts & Offers)**
- **Purpose:** Defines **active promotions** with discounts and eligibility.
- **Keys:** `id`, `name`, `promotion_rule_id`, `promotion_status_id`
- **Metrics:** `value1`, `value2`, `percentage_value`
- **Use Case:** Active promotions, discounts, campaign eligibility.

#### **6. `order_payments` (Payments)**
- **Purpose:** Tracks **order payment transactions**.
- **Keys:** `id`, `order_id`, `payment_type_id`, `transaction_number`
- **Metrics:** `amount_paid`, `status`, `qb_sync_status`
- **Use Case:** Order payments, transaction history, refunds.

#### **7. `order_shipments` (Logistics & Tracking)**
- **Purpose:** Manages **order shipments** including carriers, tracking, and costs.
- **Keys:** `id`, `order_id`, `courier_id`, `tracking_number`
- **Metrics:** `cost`, `package_count`, `status`
- **Use Case:** Shipping costs, tracking, logistics.
"""