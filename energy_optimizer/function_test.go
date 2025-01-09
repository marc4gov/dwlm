package main

import (
    "context"
    "testing"
)

func TestHandle(t *testing.T) {
    // Create test input
    input := Input{
        Profiles: make([]float32, 24),
        Prices:   make([]float32, 24),
    }
    
    // Run the function
    output, err := Handle(context.Background(), input)
    if err != nil {
        t.Fatalf("Function failed: %v", err)
    }
    
    // Check output
    if len(output.Actions) != 24 {
        t.Errorf("Expected 24 actions, got %d", len(output.Actions))
    }
}