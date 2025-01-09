import torch
import onnx
import numpy as np

def test_model_conversion():
    # 1. Load and test PyTorch model
    model = AdvancedEnergyPolicy(hidden_size=64)
    model.load_state_dict(torch.load('energy_model.pth'))
    model.eval()
    
    # Create test input
    test_profiles = torch.randn(1, 24)
    test_prices = torch.randn(1, 24)
    
    # Get PyTorch output
    with torch.no_grad():
        torch_output = model(test_profiles, test_prices)
    
    print("PyTorch model output shape:", torch_output.shape)
    
    # 2. Export to ONNX
    torch.onnx.export(model,
                     (test_profiles, test_prices),
                     "energy_model.onnx",
                     export_params=True,
                     opset_version=12,
                     do_constant_folding=True,
                     input_names=['profiles', 'prices'],
                     output_names=['actions'],
                     dynamic_axes={'profiles': {0: 'batch_size'},
                                 'prices': {0: 'batch_size'},
                                 'actions': {0: 'batch_size'}})
    
    # 3. Verify ONNX model
    onnx_model = onnx.load("energy_model.onnx")
    onnx.checker.check_model(onnx_model)
    print("ONNX model verified successfully")
    
    # 4. Test ONNX model with ONNX Runtime
    import onnxruntime as ort
    
    ort_session = ort.InferenceSession("energy_model.onnx")
    
    # Prepare inputs for ONNX Runtime
    ort_inputs = {
        'profiles': test_profiles.numpy(),
        'prices': test_prices.numpy()
    }
    
    # Run ONNX Runtime inference
    ort_output = ort_session.run(['actions'], ort_inputs)[0]
    
    print("ONNX Runtime output shape:", ort_output.shape)
    
    # Compare outputs
    np.testing.assert_allclose(torch_output.numpy(), 
                             ort_output, 
                             rtol=1e-03, 
                             atol=1e-05)
    print("PyTorch and ONNX Runtime outputs match!")

if __name__ == "__main__":
    test_model_conversion()