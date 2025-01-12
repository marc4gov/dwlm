#!/bin/bash

# Install required packages
pip install onnx onnxruntime wasmedge_pytorch

# Test PyTorch to ONNX conversion
python test_model_conversion.py

# Convert ONNX to WASM (requires WasmEdge with PyTorch backend)
wasmedgec energy_model.onnx energy_model.wasm

# Test WASM model
python test_wasm_model.py

# Test Modus integration
go test energy_function_test.go