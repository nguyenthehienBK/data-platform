package trino

import (
	"fmt"
	"log"
)

// GetStock return stock have highest price which have event "Trả cổ tức bằng tiền mặt"
func (c *Client) GetStock(event string, limit int) ([]map[string]interface{}, error) {
	// Execute the query with optional attribution headers
    query := `
	SELECT t1.stock_symbol, t1.highest FROM hudi.default.vn30 AS t1 
	INNER JOIN hudi.default.coporate_action AS t2 ON t1.stock_symbol = t2.symbol 
	WHERE t2.event_name = ?
	LIMIT ?
	`
	rows, err := c.db.Query(query, event, limit)
	if err != nil {
		return nil, fmt.Errorf("query execution failed: %w", err)
	}
	defer func() {
		if err := rows.Close(); err != nil {
			log.Printf("Error closing rows: %v", err)
		}
	}()

	// Get column names
	columns, err := rows.Columns()
	if err != nil {
		return nil, fmt.Errorf("failed to get column names: %w", err)
	}

	// Prepare result container
	results := make([]map[string]interface{}, 0)

	// Iterate through rows
	for rows.Next() {
		// Create a slice of interface{} to hold the values
		values := make([]interface{}, len(columns))
		valuePtrs := make([]interface{}, len(columns))

		// Initialize the pointers
		for i := range values {
			valuePtrs[i] = &values[i]
		}

		// Scan the row into values
		if err := rows.Scan(valuePtrs...); err != nil {
			log.Printf("Error scanning row: %v", err)
			continue
		}

		// Create a map for the current row
		rowMap := make(map[string]interface{})
		for i, col := range columns {
			val := values[i]
			rowMap[col] = val
		}

		results = append(results, rowMap)
	}

	// Check for errors after iterating
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating rows: %w", err)
	}

	return results, nil
}
