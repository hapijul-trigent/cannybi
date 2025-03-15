schema_dictionary = {
    "sales": """### Table: sales_report
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
- **sample** (0-No, 1-Yes)""",

    "orders": """### Table: orders
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
- **created_at**, **updated_at**""",

    "accounts": """### Table: accounts
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
- **account_license**, **score**, **school_email**""",

    "products": """### Table: products
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
- **portal_used_in_flag**, **canprev_codex_id**, **codex_config_module_id**""",
    "promotions": """### Table: promotions
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
- **created_at**, **updated_at**""",

    "order_payments": """### Table: order_payments
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
- **created_at**, **updated_at**""",

    "order_shipments": """### Table: order_shipments
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
- **manifest_id**"""
}
