package main

import (
    "context"
)

type Input struct {
    Profiles []float32 `json:"profiles"`
    Prices   []float32 `json:"prices"`
}

type Output struct {
    Actions []float32 `json:"actions"`
}

// Handle is the entry point for the Modus function
func Handle(ctx context.Context, input Input) (Output, error) {
    // Initialize model session (this happens only once)
    session, err := InitModel("energy_model.onnx")
    if err != nil {
        return Output{}, err
    }

    // Run inference
    result, err := session.Run([]string{"actions"}, map[string]interface{}{
        "profiles": input.Profiles,
        "prices":   input.Prices,
    })
    if err != nil {
        return Output{}, err
    }

    // Extract actions from result
    actions := result[0].Value().([]float32)
    
    return Output{Actions: actions}, nil
}