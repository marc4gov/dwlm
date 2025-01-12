import wasmedge_pytorch
import numpy as np

def test_wasm_model():
    # Load the WASM model
    runtime = wasmedge_pytorch.Runtime("energy_model.wasm")
    
    # Create test input
    test_profiles = np.random.randn(1, 24).astype(np.float32)
    test_prices = np.random.randn(1, 24).astype(np.float32)
    
    # Run inference
    wasm_output = runtime.run_inference({
        'profiles': test_profiles,
        'prices': test_prices
    })
    
    print("WASM model output shape:", wasm_output['actions'].shape)
    return wasm_output

if __name__ == "__main__":
    test_wasm_model()