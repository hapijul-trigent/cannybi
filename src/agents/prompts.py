from textwrap import dedent


SYSTEM_PROMPT_INTENTCLASSIFIER = """### TASK ###
Rephrase the user’s question using past memory and classify the intent as:
- TEXT_TO_SQL
- MISLEADING_QUERY
- TRIGGER
- GENERAL

This prompt works independently (no external reasoning or SQL generator needed).

---

### CONTEXT ###
You’ll receive:
- A current user question
- Memory with prior user questions, assistant replies, and known values (e.g., SKUs, filters, dates)

Use memory to:
- Resolve vague terms (e.g., "that product", "same as before")
- Inject known values to avoid re-querying (e.g., "Vitamin C", "2023-01-01")
- Convert date references to `YYYY-MM-DD`

---

### INSTRUCTIONS ###
1. **Rephrase the question**:
   - Use memory to fill in missing or implied details
   - Ensure clarity and schema alignment
   - Limit to **≤300 words**

2. **Classify intent**:
   - TEXT_TO_SQL: Needs data from DB using SQL
   - MISLEADING_QUERY: Vague, irrelevant, or already answered
   - TRIGGER: Calls an action (e.g., "run", "download")
   - GENERAL: Informational or casual

3. **Keep reasoning short (≤50 words)**:
   - Say what memory data you reused
   - Justify the intent label

---

### OUTPUT FORMAT ###
```json
{
  "rephrased_question": "<Updated question using memory, ≤300 words>",
  "reasoning": "<≤50 words: how memory was used and why intent fits>",
  "intent": "TEXT_TO_SQL" | "MISLEADING_QUERY" | "TRIGGER" | "GENERAL"
}```
"""

CONTEXT_SCHEMA = """
SALES DATABASE SCHEMA
### Table: sales_report
#### Purpose:
Tracks sales transactions with order, product, account, pricing, tax, and shipment details.

#### Columns:
- **id** (Primary Key)
- **order_id** (Foreign Key to orders)
- **order_item_id**
- **account_id** (Foreign Key to accounts)
- **currency_id**, **currency_abbreviation**, **currency_rate**
- **country_id**
- **account_name**, **account_type**, **account_type_id**
- **invoice**, **invoice_dt**
- **product_sku**, **product_name**, **product_description**, **product_brand**, **product_brand_id**
- **product_lot**, **product_expiry**
- **promotion_id** (Foreign Key to promotions), **promotion_name**
- **cogs**, **price**, **quantity**, **scanned_quantity**
- **discount_type**, **unit_discount**
- **line_amount**, **line_tax**
- **payterm**, **payterm_id**
- **billing_id**, **shipping_id**
- **billing_address**, **billing_city**, **billing_province**, **billing_province_id**
- **billing_lat**, **billing_log**
- **shipping_address**, **shipping_city**, **shipping_province**, **shipping_province_id**
- **shipping_lat**, **shipping_log**
- **source**, **source_id**
- **order_date**, **ship_date**
- **order_type_id**, **order_type**
- **credit_type_id**, **credit_type**
- **print_queue_date**, **completed_date**
- **purity_Id**, **new_fullscript_id**, **fullscript_id**, **fullscript_account_id**
- **iv_id**, **iv_sale_type**
- **picked_lot_codes**, **picked_date_of_expiry**
- **sample** (0-No, 1-Yes)

### Table: orders
#### Purpose:
Stores order details including payment, discounts, status, and fulfillment.

#### Columns:
- **id** (Primary Key)
- **kn_warehouse_id**
- **currency_id**, **currency_rate**
- **pod_printed**
- **account_id** (Foreign Key to accounts)
- **qb_entity_id**, **godirect_id**
- **pay_term_id** (Foreign Key to pay_terms)
- **invoice_number**
- **order_type_id** (Foreign Key to order_types)
- **order_source_id** (Foreign Key to order_sources)
- **source_value**
- **account_contact_id**
- **po_number**
- **billing_id**, **shipping_id**
- **subtotal_amount**, **coupon_discount**, **shipping_amount**
- **shipping_fee_option**, **tax_percent**, **tax_amount**, **tax_exempt**
- **total_amount**, **paid_amount**, **refund_amount**
- **total_items**, **total_lines**
- **order_status_id** (Foreign Key to order_statuses)
- **dn_sync_status**, **qb_sync_status**
- **invoice_date**, **warehouse_note**, **invoice_note**, **shipment_note**
- **claimed_by**
- **order_held**, **held_reason**, **reject_reason**
- **put_away**, **packed_percentage**, **packed_updated_at**
- **completed_date**
- **skid**, **order_split_claimed**, **order_split**, **claim_source**
- **created_by**, **updated_by**
- **created_at**, **updated_at**

### Table: accounts
#### Purpose:
Stores customer account details including contact, billing, and payment preferences.

#### Columns:
- **id** (Primary Key)
- **name**, **company_flag**
- **main_contact_name**, **country_code**
- **phone**, **extension**, **fax**, **email**, **accounting_email**
- **website**, **account_type_id** (Foreign Key to account_types)
- **tax_exempt**, **pricing_model_id**
- **school_name**, **school_id**, **graduation_year**, **graduation_month**
- **pay_term_id** (Foreign Key to pay_terms)
- **red_flag**, **stop_shipment**, **call_collect**
- **facebook_url**, **twitter_url**, **instagram_url**, **linkedin_url**
- **site_id**, **account_status_id**, **account_approval_status_id**
- **approved_date**, **created_by**, **updated_by**
- **created_at**, **updated_at**
- **last_order_date**
- **account_id**, **currency_id**, **country_id**
- **account_license**, **score**, **school_email**

### Table: products
#### Purpose:
Stores product inventory, pricing, branding, and stock.

#### Columns:
- **id** (Primary Key)
- **kn_part_id**, **kn_part_type_id**
- **name**, **pricelist_name**
- **upc**, **sku**, **erp_key**, **casecode**
- **uom**, **cogs**, **msrp**
- **line**, **brand_id** (Foreign Key to brands)
- **product_website_url**, **product_doc_url**
- **photo**, **unit_weight**, **case_length**, **case_width**, **case_height**, **case_weight**
- **case_volume**, **case_density**
- **eta_stock_from_date**, **eta_stock_to_date**
- **out_of_stock**, **safe_stock**, **instruction**
- **out_of_stock_date**, **dn_available_qty**
- **inventory_qty**, **reserved_qty**, **outbound_reserved_qty**
- **inter_wh_reserved_qty**, **kit_reserved_qty**, **account_reserved_qty**
- **hold_qty**, **expired_qty**, **ordered_qty**
- **assigned_ordered_qty**, **available_qty**, **inventory_linked**
- **size**, **serving_size**, **flavour**, **flavor**
- **codex_status**, **best_seller**, **status**, **npn**
- **include_in_portal**, **lang**, **storage_conditions**, **webinar_product**
- **canprev_used_in_flag**, **pricelist_used_in_flag**
- **created_by**, **updated_by**, **created_at**, **updated_at**
- **portal_used_in_flag**, **canprev_codex_id**, **codex_config_module_id**
### Table: promotions
#### Purpose:
Defines active promotions with discounts and eligibility.

#### Columns:
- **id** (Primary Key)
- **name**, **description**
- **from_date**, **to_date**
- **promotion_for** (0-All accounts, 1-Associations/Accounts)
- **promotion_to** (0-All products, 1-Brands/Products)
- **promotion_rule_id** (Foreign Key to promotion_rules)
- **value1**, **value2**
- **promotion_status_id** (Foreign Key to promotion_statuses)
- **approved_by**
- **priority** (0-Default, 1-High, 2-None)
- **portal** (0-No, 1-Yes)
- **rejection_reason**, **percentage_value**
- **country_id**
- **created_by**, **updated_by**
- **created_at**, **updated_at**

### Table: order_payments
#### Purpose:
Tracks order payment transactions.

#### Columns:
- **id** (Primary Key)
- **payment_type_id** (Foreign Key to payment_types)
- **transaction_type** (0-Purchase, 1-Preauth)
- **moneris_order_id** (Moneris transaction reference)
- **order_id** (Foreign Key to orders)
- **key_id**
- **transaction_number**
- **amount_paid**, **others**
- **status** (0-Failed, 1-Success, 2-Void)
- **qb_entity_id**
- **qb_sync_status** (0-No, 1-Yes)
- **qb_txn_date**
- **parent_id**
- **created_by**, **updated_by**
- **created_at**, **updated_at**

payment_types:
### Table: payment_types
#### Purpose:
Stores different types of payment methods used in transactions.

#### Columns:
- **id** (Primary Key) - Unique identifier for the payment type.
- **title** - Name of the payment type.
- **qb_entity_id** - Reference ID for QuickBooks integration.
- **created_by** - ID of the user who created the record.
- **updated_by** - ID of the user who last updated the record.
- **created_at** - Timestamp when the record was created.
- **updated_at** - Timestamp when the record was last updated.


### Table: order_shipments
#### Purpose:
Manages order shipments including carriers, tracking, and costs.

#### Columns:
- **id** (Primary Key)
- **order_id** (Foreign Key to orders)
- **scheduled_date**
- **weight**, **uom** (0-Kg, 1-Lbs)
- **cost**
- **package_count**
- **courier_id** (Foreign Key to couriers)
- **tracking_number**
- **courier_response_id**
- **pickup_id**
- **status** (0-Deleted, 1-Active)
- **warehouse_id** (Foreign Key to warehouses)
- **bol_file_name**
- **created_by**, **updated_by**
- **created_at**, **updated_at**
- **manifest_id**
"""


CONTEXT_SCHEMA = """<Sales Schema>
-- canprevcommons3_stg.sales_report definition

CREATE TABLE `sales_report` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `order_id` bigint unsigned NOT NULL DEFAULT '0',
  `order_item_id` bigint DEFAULT NULL,
  `account_id` bigint unsigned NOT NULL,
  `currency_id` smallint unsigned NOT NULL DEFAULT '1',
  `currency_abbreviation` varchar(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'CAD',
  `currency_rate` double NOT NULL DEFAULT '1',
  `country_id` int unsigned DEFAULT '39',
  `account_name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `account_type` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `account_type_id` int DEFAULT NULL,
  `invoice` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `invoice_dt` timestamp NULL DEFAULT NULL,
  `product_sku` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `product_name` varchar(500) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `product_description` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `product_brand` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `product_brand_id` bigint DEFAULT NULL,
  `product_lot` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `product_expiry` datetime DEFAULT NULL,
  `promotion_id` bigint DEFAULT NULL,
  `promotion_name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `cogs` decimal(10,2) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `quantity` bigint DEFAULT NULL,
  `scanned_quantity` int DEFAULT NULL,
  `discount_type` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `unit_discount` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `line_amount` decimal(10,2) DEFAULT NULL,
  `line_tax` decimal(10,2) DEFAULT NULL,
  `payterm` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `payterm_id` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `billing_id` bigint DEFAULT NULL,
  `shipping_id` bigint DEFAULT NULL,
  `billing_address` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `billing_city` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `billing_province` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `billing_province_id` int unsigned DEFAULT NULL,
  `billing_lat` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `billing_log` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `shipping_address` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `shipping_city` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `shipping_province` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `shipping_province_id` int unsigned DEFAULT NULL,
  `shipping_lat` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `shipping_log` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `source` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `source_id` bigint DEFAULT NULL,
  `order_date` timestamp NULL DEFAULT NULL,
  `ship_date` timestamp NULL DEFAULT NULL,
  `order_type_id` bigint DEFAULT NULL,
  `order_type` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `credit_type_id` tinyint DEFAULT NULL,
  `credit_type` varchar(100) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `print_queue_date` timestamp NULL DEFAULT NULL,
  `completed_date` timestamp NULL DEFAULT NULL,
  `purity_Id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `new_fullscript_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `fullscript_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `fullscript_account_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `iv_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `iv_sale_type` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `picked_lot_codes` varchar(255) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `picked_date_of_expiry` varchar(255) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `sample` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-No 1-Yes',
  PRIMARY KEY (`id`),
  KEY `order_date_index` (`order_date`),
  KEY `order_id_index` (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5502806 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;


-- canprevcommons3_stg.orders definition
CREATE TABLE `orders` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `kn_warehouse_id` smallint unsigned DEFAULT NULL,
  `currency_id` smallint unsigned NOT NULL DEFAULT '1',
  `currency_rate` double NOT NULL DEFAULT '1',
  `pod_printed` tinyint(1) DEFAULT '0',
  `account_id` bigint unsigned NOT NULL,
  `qb_entity_id` bigint unsigned NOT NULL,
  `godirect_id` bigint unsigned DEFAULT NULL,
  `pay_term_id` int unsigned DEFAULT NULL,
  `invoice_number` bigint unsigned NOT NULL,
  `order_type_id` tinyint unsigned NOT NULL,
  `order_source_id` tinyint unsigned NOT NULL,
  `source_value` bigint unsigned DEFAULT NULL,
  `account_contact_id` bigint unsigned NOT NULL,
  `po_number` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `billing_id` bigint unsigned NOT NULL,
  `shipping_id` bigint unsigned NOT NULL,
  `subtotal_amount` double NOT NULL,
  `coupon_discount` double NOT NULL COMMENT 'Coupon discount',
  `shipping_amount` double NOT NULL,
  `shipping_fee_option` tinyint unsigned NOT NULL,
  `tax_percent` double NOT NULL,
  `tax_amount` double NOT NULL,
  `tax_exempt` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-No 1-Yes',
  `total_amount` double NOT NULL,
  `paid_amount` double NOT NULL,
  `refund_amount` double NOT NULL,
  `total_items` smallint unsigned NOT NULL,
  `total_lines` smallint unsigned NOT NULL,
  `order_status_id` tinyint unsigned NOT NULL,
  `dn_sync_status` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-No 1-Yes',
  `qb_sync_status` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-No 1-Yes',
  `invoice_date` timestamp NULL DEFAULT NULL,
  `warehouse_note` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `invoice_note` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `shipment_note` text COLLATE utf8mb4_unicode_ci,
  `claimed_by` bigint unsigned DEFAULT NULL,
  `order_held` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-No 1-Yes',
  `held_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `reject_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `put_away` tinyint unsigned NOT NULL DEFAULT '0',
  `packed_percentage` float unsigned NOT NULL DEFAULT '0',
  `packed_updated_at` timestamp NULL DEFAULT NULL,
  `completed_date` timestamp NULL DEFAULT NULL,
  `skid` tinyint NOT NULL DEFAULT '0' COMMENT '0-No Skid 1-Skid',
  `order_split_claimed` tinyint unsigned DEFAULT '0',
  `order_split` smallint unsigned DEFAULT '1',
  `claim_source` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-CPC 1-CONVOY',
  `created_by` bigint unsigned NOT NULL,
  `updated_by` bigint unsigned NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `orders_account_id_foreign` (`account_id`),
  KEY `orders_pay_term_id_foreign` (`pay_term_id`),
  KEY `orders_order_type_id_foreign` (`order_type_id`),
  KEY `orders_order_source_id_foreign` (`order_source_id`),
  KEY `orders_account_contact_id_foreign` (`account_contact_id`),
  KEY `orders_order_status_id_foreign` (`order_status_id`),
  KEY `kn_warehouse_id` (`kn_warehouse_id`),
  CONSTRAINT `orders_order_source_id_foreign` FOREIGN KEY (`order_source_id`) REFERENCES `order_sources` (`id`),
  CONSTRAINT `orders_order_status_id_foreign` FOREIGN KEY (`order_status_id`) REFERENCES `order_statuses` (`id`),
  CONSTRAINT `orders_order_type_id_foreign` FOREIGN KEY (`order_type_id`) REFERENCES `order_types` (`id`),
  CONSTRAINT `orders_pay_term_id_foreign` FOREIGN KEY (`pay_term_id`) REFERENCES `pay_terms` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=503480 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- canprevcommons3_stg.accounts definition
CREATE TABLE `accounts` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `company_flag` tinyint NOT NULL DEFAULT '0' COMMENT '0 => Canprev, 1 => Apotex',
  `main_contact_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `country_code` smallint unsigned DEFAULT NULL,
  `phone` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `extension` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fax` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `accounting_email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `website` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `account_type_id` int unsigned NOT NULL,
  `tax_exempt` tinyint unsigned DEFAULT '0' COMMENT '0-No 1-Yes',
  `pricing_model_id` int unsigned NOT NULL,
  `school_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `school_id` int unsigned DEFAULT NULL,
  `graduation_year` int unsigned DEFAULT NULL,
  `graduation_month` tinyint unsigned DEFAULT NULL,
  `pay_term_id` int unsigned DEFAULT NULL,
  `red_flag` tinyint unsigned DEFAULT '0' COMMENT '0-No 1-Yes',
  `stop_shipment` tinyint unsigned DEFAULT '0' COMMENT '0-No 1-Yes',
  `call_collect` tinyint unsigned DEFAULT '0' COMMENT '0-No 1-Yes',
  `facebook_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'N/A',
  `twitter_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'N/A',
  `instagram_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'N/A',
  `linkedin_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'N/A',
  `site_id` int unsigned NOT NULL DEFAULT '0',
  `account_status_id` int unsigned NOT NULL,
  `account_approval_status_id` int unsigned NOT NULL DEFAULT '0',
  `approved_date` timestamp NULL DEFAULT NULL,
  `created_by` bigint unsigned NOT NULL,
  `updated_by` bigint unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `last_order_date` datetime DEFAULT NULL,
  `account_id` bigint unsigned DEFAULT '0',
  `currency_id` smallint unsigned NOT NULL DEFAULT '1',
  `country_id` int unsigned NOT NULL DEFAULT '39',
  `account_license` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `score` bigint DEFAULT '0',
  `school_email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `accounts_account_type_id_foreign` (`account_type_id`),
  KEY `accounts_pricing_model_id_foreign` (`pricing_model_id`),
  KEY `accounts_pay_term_id_foreign` (`pay_term_id`),
  KEY `accounts_account_status_id_index` (`account_status_id`),
  KEY `accounts_account_approval_status_id_index` (`account_approval_status_id`),
  KEY `accounts_school_id_foreign` (`school_id`),
  KEY `currency_id` (`currency_id`),
  KEY `country_id` (`country_id`),
  FULLTEXT KEY `accounts_fts_idx` (`name`,`main_contact_name`,`phone`,`fax`,`email`),
  CONSTRAINT `accounts_account_type_id_foreign` FOREIGN KEY (`account_type_id`) REFERENCES `account_types` (`id`),
  CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `accounts_ibfk_2` FOREIGN KEY (`country_id`) REFERENCES `countries` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `accounts_pay_term_id_foreign` FOREIGN KEY (`pay_term_id`) REFERENCES `pay_terms` (`id`),
  CONSTRAINT `accounts_pricing_model_id_foreign` FOREIGN KEY (`pricing_model_id`) REFERENCES `pricing_models` (`id`),
  CONSTRAINT `accounts_school_id_foreign` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=47738 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- canprevcommons3_stg.products definition

CREATE TABLE `products` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `kn_part_id` bigint unsigned DEFAULT NULL,
  `kn_part_type_id` tinyint unsigned DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `pricelist_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `upc` bigint unsigned DEFAULT NULL,
  `sku` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `erp_key` bigint unsigned DEFAULT NULL,
  `casecode` bigint unsigned DEFAULT NULL,
  `uom` bigint unsigned DEFAULT NULL,
  `cogs` double DEFAULT NULL,
  `msrp` double DEFAULT NULL,
  `line` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `brand_id` int unsigned DEFAULT NULL,
  `product_website_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_doc_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `photo` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `unit_weight` double DEFAULT '0',
  `case_length` double unsigned DEFAULT '0',
  `case_width` double unsigned DEFAULT '0',
  `case_height` double unsigned DEFAULT '0',
  `case_weight` double unsigned DEFAULT '0',
  `case_volume` double unsigned DEFAULT '0',
  `case_density` double unsigned DEFAULT '0',
  `eta_stock_from_date` date DEFAULT NULL,
  `eta_stock_to_date` date DEFAULT NULL,
  `out_of_stock` tinyint unsigned DEFAULT '0' COMMENT '0-No 1-Yes',
  `safe_stock` int unsigned DEFAULT '0',
  `instruction` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `out_of_stock_date` datetime DEFAULT NULL,
  `dn_available_qty` bigint unsigned NOT NULL DEFAULT '0',
  `inventory_qty` bigint unsigned NOT NULL,
  `reserved_qty` bigint unsigned NOT NULL,
  `outbound_reserved_qty` bigint unsigned NOT NULL DEFAULT '0',
  `inter_wh_reserved_qty` bigint unsigned NOT NULL DEFAULT '0',
  `kit_reserved_qty` bigint unsigned NOT NULL DEFAULT '0',
  `account_reserved_qty` bigint unsigned NOT NULL,
  `hold_qty` bigint unsigned NOT NULL DEFAULT '0',
  `expired_qty` bigint unsigned NOT NULL DEFAULT '0',
  `ordered_qty` bigint unsigned NOT NULL,
  `assigned_ordered_qty` bigint unsigned NOT NULL DEFAULT '0',
  `available_qty` bigint NOT NULL,
  `inventory_linked` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-Inventory Not Linked 1-Inventory Linked',
  `size` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `serving_size` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `flavour` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `flavor` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `codex_status` tinyint unsigned NOT NULL,
  `best_seller` int unsigned DEFAULT NULL,
  `status` tinyint unsigned DEFAULT '0' COMMENT '0-Inactive 1-Active',
  `npn` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `include_in_portal` tinyint unsigned DEFAULT '1' COMMENT '0-No 1-Yes',
  `lang` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `storage_conditions` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `webinar_product` tinyint DEFAULT '0',
  `canprev_used_in_flag` tinyint unsigned DEFAULT NULL,
  `created_by` bigint unsigned DEFAULT NULL,
  `pricelist_used_in_flag` tinyint unsigned DEFAULT NULL,
  `updated_by` bigint unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `portal_used_in_flag` tinyint unsigned DEFAULT NULL,
  `canprev_codex_id` bigint unsigned DEFAULT NULL,
  `codex_config_module_id` tinyint unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `products_brand_id_foreign` (`brand_id`),
  KEY `kn_part_id` (`kn_part_id`),
  KEY `kn_part_type_id` (`kn_part_type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3629 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- canprevcommons3_stg.promotions definition
CREATE TABLE `promotions` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `from_date` date NOT NULL,
  `to_date` date NOT NULL,
  `promotion_for` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-All accounts 1-Associations/Accounts',
  `promotion_to` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-All products 1-Brands/Products',
  `promotion_rule_id` int unsigned NOT NULL,
  `value1` double NOT NULL,
  `value2` double DEFAULT NULL,
  `promotion_status_id` int unsigned NOT NULL,
  `approved_by` bigint unsigned DEFAULT NULL,
  `priority` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-Default 1-High 2-None',
  `portal` tinyint unsigned NOT NULL DEFAULT '1' COMMENT '0-No 1-Yes',
  `rejection_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `percentage_value` double NOT NULL DEFAULT '0',
  `country_id` int unsigned DEFAULT NULL,
  `created_by` bigint unsigned NOT NULL,
  `updated_by` bigint unsigned NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `promotions_promotion_rule_id_foreign` (`promotion_rule_id`),
  KEY `promotions_promotion_status_id_foreign` (`promotion_status_id`),
  CONSTRAINT `promotions_promotion_rule_id_foreign` FOREIGN KEY (`promotion_rule_id`) REFERENCES `promotion_rules` (`id`),
  CONSTRAINT `promotions_promotion_status_id_foreign` FOREIGN KEY (`promotion_status_id`) REFERENCES `promotion_statuses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=835 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- canprevcommons3_stg.order_payments definition

CREATE TABLE `order_payments` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `payment_type_id` tinyint unsigned NOT NULL,
  `transaction_type` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-purchase 1-preauth',
  `moneris_order_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Moneris order ID',
  `order_id` bigint unsigned NOT NULL,
  `key_id` bigint unsigned NOT NULL,
  `transaction_number` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount_paid` double NOT NULL,
  `others` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` tinyint unsigned NOT NULL DEFAULT '1' COMMENT '0-Failed 1-Success 2-Void',
  `qb_entity_id` bigint unsigned NOT NULL,
  `qb_sync_status` tinyint unsigned NOT NULL COMMENT '0-No 1-Yes',
  `qb_txn_date` date DEFAULT NULL,
  `parent_id` bigint unsigned DEFAULT NULL,
  `created_by` bigint unsigned NOT NULL,
  `updated_by` bigint unsigned NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `order_payments_payment_type_id_foreign` (`payment_type_id`),
  KEY `order_payments_order_id_foreign` (`order_id`),
  CONSTRAINT `order_payments_order_id_foreign` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `order_payments_payment_type_id_foreign` FOREIGN KEY (`payment_type_id`) REFERENCES `payment_types` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19392 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- canprevcommons3_stg.order_shipments definition

CREATE TABLE `order_shipments` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `order_id` bigint unsigned NOT NULL,
  `scheduled_date` date DEFAULT NULL,
  `weight` double NOT NULL,
  `uom` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-Kg 1-Lbs',
  `cost` double NOT NULL,
  `package_count` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `courier_id` tinyint unsigned NOT NULL,
  `tracking_number` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `courier_response_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pickup_id` bigint unsigned DEFAULT NULL,
  `status` tinyint unsigned DEFAULT '1' COMMENT '0-Deleted 1-Active',
  `warehouse_id` smallint unsigned NOT NULL,
  `bol_file_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` bigint unsigned NOT NULL,
  `updated_by` bigint unsigned NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `manifest_id` bigint unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `order_shipments_order_id_foreign` (`order_id`),
  KEY `order_shipments_courier_id_foreign` (`courier_id`),
  KEY `order_shipments_warehouse_id_foreign` (`warehouse_id`),
  CONSTRAINT `order_shipments_courier_id_foreign` FOREIGN KEY (`courier_id`) REFERENCES `couriers` (`id`),
  CONSTRAINT `order_shipments_order_id_foreign` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `order_shipments_warehouse_id_foreign` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=126739 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


SYSTEM_PROMPT_SQL_REASONING = """### TASK ###
You are a skilled data analyst who deeply reasons about the user's question and the database schema to provide a structured reasoning plan.

### INSTRUCTIONS ###
1. Carefully analyze the user’s question and the provided database schema.
2. Provide a **clear, numbered reasoning plan** that aligns logically with the SQL query to be generated. Only include **necessary and relevant reasoning**.
3. Maintain the same **language** used in the user's question.
4. If the question involves **time-based filtering**, extract the **current date** from the user's input or assume it if mentioned.
5. Determine the **last quarter** based on the current date if required:
   - Q1 (Jan–Mar) → Last quarter: Q4 (Oct–Dec, previous year)
   - Q2 (Apr–Jun) → Last quarter: Q1 (Jan–Mar, same year)
   - Q3 (Jul–Sep) → Last quarter: Q2 (Apr–Jun, same year)
   - Q4 (Oct–Dec) → Last quarter: Q3 (Jul–Sep, same year)
6. Clearly state the **start and end dates** of the last quarter if applicable.
7. **Do NOT include SQL code** in the reasoning.
8. Ensure the output is a **valid JSON object** only.

### OUTPUT FORMAT (Strictly Valid JSON) ###
Return the result using this exact structure:

```json
{
  "reasoning_plan": "<Step-by-step logical reasoning aligned with SQL generation, in the user's language>",
  "last_quarter_start_date": "<YYYY-MM-DD>",
  "last_quarter_end_date": "<YYYY-MM-DD>"
}```
"""


# SYSTEM_PROMPT_SQL_REASONING = """### TASK ###
# You are a skilled data analyst who uses both the current question and past conversation history to extract **all required context** for writing a structured reasoning plan that leads to an accurate SQL query.

# ### CONTEXT ###
# The memory buffer contains the user’s past questions, your answers, and system messages (if any). Use this context to:
# - Understand what the user is referring to (even indirectly)
# - Extract relevant filters, table references, and data requirements mentioned earlier
# - Identify entities, timeframes, or conditions previously discussed but not repeated in the current question

# ### INSTRUCTIONS ###
# 1. Analyze the **user's current question**, the **provided database schema**, and the **past chat history (memory)**.
# 2. Extract all relevant information from prior messages that may be **required for accurate SQL generation**, including:
#    - Previously mentioned table names, fields, filters, groupings, timeframes
#    - Business entities like countries, departments, products
#    - Logical intent across turns (follow-ups, comparisons, etc.)
# 3. Provide a **clear, numbered reasoning plan** aligned with the SQL logic. Keep it concise and focused.
# 4. Preserve the **language used by the user** in the latest question.
# 5. If the task involves **time-based filtering**, infer the **current date** (from the user or context), and determine the **last quarter**:
#    - Q1 (Jan–Mar) → Last quarter: Q4 (Oct–Dec, previous year)
#    - Q2 (Apr–Jun) → Last quarter: Q1 (Jan–Mar, same year)
#    - Q3 (Jul–Sep) → Last quarter: Q2 (Apr–Jun, same year)
#    - Q4 (Oct–Dec) → Last quarter: Q3 (Jul–Sep, same year)
# 6. Clearly state the **start and end dates** of the last quarter if applicable.
# 7. **Do NOT generate SQL** — just reason step by step toward it.
# 8. Output must be a **valid JSON object**, nothing else.

# ### OUTPUT FORMAT (Strictly Valid JSON) ###
# Return the result using this exact structure:

# ```json
# {
#   "reasoning_plan": "<Step-by-step logical reasoning aligned with SQL generation, in the user's language>",
#   "last_quarter_start_date": "<YYYY-MM-DD>",
#   "last_quarter_end_date": "<YYYY-MM-DD>"
# }```
# """

LANGUAGE =  'english'


SYSTEM_PROMPT_SQG = """### TASK ###
Generate **accurate MySQL-compatible SQL queries** based on the user’s current question, past conversation memory, database schema, and structured reasoning steps.

### CONTEXT ###
You may be provided with prior conversation history (memory). Use it to:
- Retrieve earlier user requirements, filters, table references, or entities
- Connect follow-up questions with earlier instructions, answers may be useful to optimize query instead querying same info again when it is available with previous answer such as product names, SKU, etc....
- Generate queries that reflect the **entire intent**, not just the most recent message

### INSTRUCTIONS ###
1. Carefully analyze:
   - The **database schema**
   - The **reasoning steps**
   - The **past and current conversation context (memory)** and fetch if question refering to answer of previous answer.
   "1. Analyze the user’s question and identify relevant database fields.\n"
   "2. Determine if the query requires filtering by time.\n"
   "3. If time-based, extract the current date and calculate the last quarter’s date range:\n"
   "   - Q1 (Jan-Mar) → Last quarter: Q4 (Oct-Dec, previous year)\n"
   "   - Q2 (Apr-Jun) → Last quarter: Q1 (Jan-Mar, same year)\n"
   "   - Q3 (Jul-Sep) → Last quarter: Q2 (Apr-Jun, same year)\n"
   "   - Q4 (Oct-Dec) → Last quarter: Q3 (Jul-Sep, same year)\n"
   "4. Construct the SQL query with the appropriate conditions for filtering, aggregation, and ordering.\n"
   "5. Ensure the query is optimized for performance (e.g., using indexed fields, avoiding unnecessary joins).\n\n"
2. For each reasoning step that requires SQL:
   - Generate a **correct and valid MySQL query**
   - **Skip reasoning steps** that do not need a query (do not include nulls or placeholders)

3. Ensure that each query:
   - Is syntactically and logically correct for **MySQL**
   - Reflects the **true user intent** (even if pieces of it were mentioned earlier)
   - Uses only **defined tables and columns** from the schema

4. Optimize query performance:
   - Use **indexed fields** in `WHERE`, `JOIN`, or `GROUP BY`
   - Prefer **explicit `JOIN` clauses**
   - Avoid unnecessary subqueries; **combine steps when possible**
   - Use **`LIMIT 10`** by default unless otherwise specified

5. Follow **MySQL best practices and constraints**:
   ✅ Use correct aliasing and joins  
   ❌ Avoid non-MySQL syntax or functions  
   ❌ Never use `LIMIT` directly inside subqueries used by `IN`, `ALL`, etc.  
   ✅ Instead, rewrite such logic with `JOIN` or CTE-style subqueries

6. Apply any **time-based filtering**, **aggregation**, or **grouping** as described in the reasoning step — even if inferred from memory.

### OUTPUT FORMAT (Strict Valid JSON) ###
Return only a JSON object in the format below — one accurate SQL query per relevant reasoning step:

```json
{
  "sql_query_steps": [
    {
      "reason": "<Reasoning step that requires a query>",
      "query": "<Accurate, valid MySQL SQL query>"
    }
  ]
}```
"""


SYSTEM_PROMPT_BI_ANALYSIS = """### ROLE ###
You are a Business Intelligence (BI) expert specializing in data analysis and deriving actionable insights.

### TASK ###
Analyze SQL query results, extract meaningful business insights, summarize key findings clearly, and generate visualizations only when necessary.

### INSTRUCTIONS ###
1. **Per SQL Query Step**:
   - Extract only the **relevant business insights** from the result.
   - Focus on **how the result impacts business decisions or performance**.

2. **Final Report**:
   - Provide a **concise Business Intelligence summary** combining all SQL query steps.
   - Include a **Key Results Table** only if it adds business value.
   - Add **clear, actionable recommendations** that are data-driven.
   - Suggest **follow-up questions** that could guide further analysis, based on the current results and schema.
   - The full summary must be in **clean Markdown format**. Make sure to include reuired infromation from analysis summary for the followup questions, so will be used to query the database.

3. **Visualization**:
   - If needed to understand the data visually, include **Python code** using **seaborn** and **matplotlib**.
   - Chart types: `"line"`, `"multi_line"`, `"bar"`, `"pie"`, `"grouped_bar"`, `"stacked_bar"`, `"area"`.
   - Save the chart(s) to a `charts/` folder with **meaningful filenames**.
   - **DO NOT** use `plt.show()` — only save the chart using `plt.savefig()`.
   - If a chart is **not needed**, return `"chart-python-code": "None"`.

### OUTPUT FORMAT (Strict JSON Only) ###
Return only a valid JSON with the following structure:

```json
{
  "business_analysis": {
    "summary": "<BI insights in Markdown format, clearly written and structured>",
    "chart-python-code": "<Seaborn & Matplotlib Python code if chart is needed, otherwise 'None'>",
    "result": "<false if any error occured else true>"
  }
}```
"""



SYTEM_PROMPT_MISLEADING_QUERY_SUGGESTION = dedent(f"""
### TASK ###
Rephrase the user's question into **5 relevant, answerable questions** based on the database schema.

### INSTRUCTIONS ###
1. **Analyze the schema** and **reason why the original question is misleading**.
2. **Suggest 3 alternative questions** that can be answered using the schema.
3. **Avoid requiring external data sources (e.g., CAC, third-party analytics).**
4. **Ensure the new questions are SQL-compatible** and return structured results.
5. **Format the response in markdown for chat output.**

### DATABASE SCHEMA ###
{CONTEXT_SCHEMA}

### OUTPUT FORMAT (Valid Markdown) ###

**❌ Original Question:** _<Original Question>_

**🔍 Why It’s Misleading:**  
_<Explanation>_

**✅ Suggested Questions:**  
1. _<Revised Question 1>_  
2. _<Revised Question 2>_  
3. _<Revised Question 3>_
4. _<Revised Question 4>_
5. _<Revised Question 5>_
""")

