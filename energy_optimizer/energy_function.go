package main

import (
    "github.com/hypermodeinc/modus/pkg/models"
)

// EnergyInput represents the expected input structure
type EnergyInput struct {
    Profiles []float32 `json:"profiles"`
    Prices   []float32 `json:"prices"`
}

// EnergyOutput represents the model output
type EnergyOutput struct {
    Actions []float32 `json:"actions"`
}

// InvokeModel calls the energy optimization model
func InvokeModel(input EnergyInput) (EnergyOutput, error) {
    // Create model options
    opts := models.Options{
        ModelPath: "energy_model.wasm",
    }
    
    // Invoke the model
    result, err := models.Invoke(opts, input)
    if err != nil {
        return EnergyOutput{}, err
    }
    
    // Parse and return results
    var output EnergyOutput
    err = result.Decode(&output)
    return output, err
}