query:
 	select ;

select:
	SELECT select_from FROM BUCKET_NAME WHERE complex_condition;

create_index:
	CREATE INDEX INDEX_NAME ON BUCKET_NAME(FIELD_LIST) WHERE complex_condition |
	CREATE INDEX INDEX_NAME ON BUCKET_NAME(complex_condition) |
	CREATE INDEX INDEX_NAME ON BUCKET_NAME(USER_FIELD_LIST);

select_from:
	* | COUNT(*) |  COUNT( DISTINCT field ) | SUM( non_string_field ) | SUM(DISTINCT non_string_field ) | MAX( non_string_field ) | MIN( non_string_field );

complex_condition:
	(condition) AND (condition) | (condition) OR (condition) | condition;

condition:
	numeric_condition | string_condition ;

field:
	NUMERIC_FIELD | STRING_FIELD;

non_string_field:
	NUMERIC_FIELD;

order_by:
	field_list;

# NUMERIC RULES

numeric_condition:
    numeric_closed_range |
	numeric_between_condition |
	numeric_equals_condition ;

numeric_equals_condition:
	numeric_field = numeric_value ;

numeric_between_condition:
	NUMERIC_FIELD BETWEEN LOWER_BOUND_VALUE and UPPER_BOUND_VALUE;

numeric_closed_range:
    CLOSED_RANGE_NUMERIC_FIELD > LOWER_BOUND_VALUE and SAME_CLOSED_RANGE_NUMERIC_FIELD < UPPER_BOUND_VALUE |
    CLOSED_RANGE_NUMERIC_FIELD >= LOWER_BOUND_VALUE and SAME_CLOSED_RANGE_NUMERIC_FIELD <= UPPER_BOUND_VALUE |
    CLOSED_RANGE_NUMERIC_FIELD >= LOWER_BOUND_VALUE and SAME_CLOSED_RANGE_NUMERIC_FIELD < UPPER_BOUND_VALUE |
    CLOSED_RANGE_NUMERIC_FIELD > LOWER_BOUND_VALUE and SAME_CLOSED_RANGE_NUMERIC_FIELD <= UPPER_BOUND_VALUE;

numeric_field_list:
	LIST;

numeric_field:
	NUMERIC_FIELD;

numeric_value:
	NUMERIC_VALUE;

# STRING RULES

string_condition:
	string_like_condition |
	string_between_condition |
	string_equals_condition  ;

string_equals_condition:
	string_field = string_values;

string_between_condition:
	string_field BETWEEN LOWER_BOUND_VALUE and UPPER_BOUND_VALUE;

string_like_condition:
	string_field LIKE 'STRING_VALUES%' | string_field LIKE STRING_VALUES;

string_field:
	STRING_FIELD;

string_values:
	STRING_VALUES;

field_list:
	NUMERIC_FIELD_LIST | STRING_FIELD_LIST | NUMERIC_FIELD_LIST, STRING_FIELD_LIST ;
