package main

import (
    "testing"
    "github.com/hypermodeinc/modus/pkg/models"
)

func TestEnergyModel(t *testing.T) {
    input := EnergyInput{
        Profiles: make([]float32, 24),
        Prices:   make([]float32, 24),
    }
    
    output, err := InvokeModel(input)
    if err != nil {
        t.Fatalf("Model invocation failed: %v", err)
    }
    
    if len(output.Actions) != 24 {
        t.Errorf("Expected 24 actions, got %d", len(output.Actions))
    }
}