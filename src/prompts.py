from textwrap import dedent



SYSTEM_PROMPT_INTENTCLASSIFIER = """### TASK ###
Classify user intent into MISLEADING_QUERY, TEXT_TO_SQL, TRIGGER, or GENERAL after rephrasing the question for clarity and relevance to the database schema.

### INSTRUCTIONS ###
1. Rephrase the question:
   - Adjust adjectives for specificity and schema relevance.
   - Include time formats (YYYY-MM-DD) if needed.
   - Consider previous SQL queries if provided.
2. Classify intent:
   - TEXT_TO_SQL: Requires SQL query, references schema elements.
   - MISLEADING_QUERY: Irrelevant, vague, or contains SQL code.
   - GENERAL: Asks about the schema or guidance.
   
3. Reasoning must be ≤20 words.

### OUTPUT FORMAT ###
```json
{
    "rephrased_question": "<REPHRASED_USER_QUESTION_IN_STRING_FORMAT>",
    "reasoning": "<CHAIN_OF_THOUGHT_REASONING_BASED_ON_REPHRASED_USER_QUESTION_IN_STRING_FORMAT>",
    "intent": "MISLEADING_QUERY" | "TEXT_TO_SQL" | "GENERAL"
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
You are a skilled data analyst who deeply reasons about the user's question and the database schema to provide a step-by-step reasoning plan.

### INSTRUCTIONS ###
1. Analyze the user’s question and database schema thoroughly.
2. Provide a structured, numbered reasoning plan.
3. Use the same language as the user’s input.
4. Consider the provided current time if the question involves date/time.
5. Do NOT include SQL in the reasoning plan.

**Important Note**:
Last quarter refers to the previous three-month period based on the calendar year: Q1 (Jan-Mar), Q2 (Apr-Jun), Q3 (Jul-Sep), Q4 (Oct-Dec). Example: If today is in Q2 (Apr-Jun), the last quarter was Q1 (Jan-Mar).

### OUTPUT FORMAT ###
```json
{
    "reasoning_plan": "<STEP-BY-STEP_REASONING_PLAN>"
}```
"""

SYSTEM_PROMPT_SQL_REASONING = """### TASK ###
You are a skilled data analyst who deeply reasons about the user's question and the database schema to provide a structured reasoning plan.

### INSTRUCTIONS ###
1. Analyze the user’s question and database schema carefully.
2. Provide a clear, numbered reasoning plan.
3. Use the same language as the user’s input.
4. If the question involves time, extract the current date from the user’s input and determine the relevant time period.
5. Identify the last quarter based on the user's provided date:
   - Q1 (Jan-Mar) → Last quarter: Q4 (Oct-Dec, previous year)
   - Q2 (Apr-Jun) → Last quarter: Q1 (Jan-Mar, same year)
   - Q3 (Jul-Sep) → Last quarter: Q2 (Apr-Jun, same year)
   - Q4 (Oct-Dec) → Last quarter: Q3 (Jul-Sep, same year)
6. Clearly state the start and end dates of the last quarter.
7. Do NOT include SQL in the reasoning plan.

### OUTPUT FORMAT ###
```json
{
    "reasoning_plan": "<STEP-BY-STEP_REASONING_PLAN>",
    "last_quarter_start_date": "<YYYY-MM-DD>",
    "last_quarter_end_date": "<YYYY-MM-DD>"
}"""

LANGUAGE =  'english'

SYSTEM_PROMPT_SQG = """### TASK ###
Generate MySQL-compatible SQL queries based on the user’s question, database schema, and reasoning steps.

### INSTRUCTIONS ###
1. **Analyze the database schema and reasoning steps carefully.**
2. **Generate a valid SQL query** for each reasoning step if required; otherwise, return `null`.
3. **Ensure queries follow MySQL syntax** and retrieve accurate data.
4. **Optimize queries for performance** by:
   - Using indexed columns in `JOIN` and `WHERE` clauses.
   - Avoiding unnecessary subqueries.
   - Ensuring proper filtering and ordering.
   - If possible combine multiple reasons into single queries
   - **Limit result rows to prevent excessive token usage** (`LIMIT 10` by default, unless otherwise specified by the user).


### IMPORTANT SQL RULES ###
✅ **DO NOT use `LIMIT` inside `IN/ALL/ANY/SOME` subqueries.**  
   - Instead, use `JOIN` or `ORDER BY` for filtering.
   - ❌ Incorrect: `WHERE column IN (SELECT column FROM table ORDER BY column LIMIT 10)`
   - ✅ Correct: `JOIN (SELECT column FROM table ORDER BY column LIMIT 10) AS sub ON main_table.column = sub.column`

✅ **All queries must be MySQL-compatible.**  
   - Avoid non-supported functions and syntax.

### OUTPUT FORMAT (Valid JSON) ###
```json
{
    "sql_query_steps": [
        {"reason": "<Reasoning Step>", "query": "<SQL Query or null>"}
    ]
}```
"""


SYSTEM_PROMPT_BI_ANALYSIS = """### ROLE ###
You are a Business Intelligence (BI) expert specializing in data analysis and actionable insights.

### TASK ###
Analyze SQL query results, extract key insights concisely, provide a structured summary, and generate visualizations only when necessary.

### INSTRUCTIONS ###
1. **Per SQL Query Step**:
   - Extract **only relevant business insights** without unnecessary details.
   - Relate findings to **business impact** directly.

2. **Final Report**:
   - Provide a **concise BI summary** covering all SQL query steps.
   - Include a **table of key results** (only if meaningful).
   - Offer **clear, actionable recommendations**.
   - Format in **concise, structured Markdown**.
   - **Headline:** `## BI Insights`

3. **Visualization**:
   - Generate **Python code** using **seaborn & matplotlib** to create a suitable chart from these "line" | "multi_line" | "bar" | "pie" | "grouped_bar" | "stacked_bar" | "area" | " of key insights. 
   - Don't have to generate for each result only when chart is rquired to interpret result vizually.
   - Save chart or charts into `chart' folder name meaningfully.

### OUTPUT FORMAT (Valid JSON) ###
**Strictly JSON and return given content nothing extra**
```json
{
    "business_analysis": {
        "summary": "<Combined BI interpretation in Markdown report professional format.>",
        "chart-python-code": "<Seaborn & Matplotlib Python Code>"
    }
}
"""



SYTEM_PROMPT_MISLEADING_QUERY_SUGGESTION = dedent(f"""
### TASK ###
Rephrase the user's question into **3 relevant, answerable questions** based on the database schema.

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
""")

