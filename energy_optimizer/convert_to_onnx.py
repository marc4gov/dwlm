import torch
from energy_policy import AdvancedEnergyPolicy
import os

def convert_to_onnx(model_path='energy_model.pth', output_path='energy_model.onnx'):
    # Load model
    model = AdvancedEnergyPolicy(hidden_size=64)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    # Create dummy input (based on your existing model's expected input)
    dummy_profiles = torch.randn(1, 24)  # Single day, 24 hours
    dummy_prices = torch.randn(1, 24)    # Single day, 24 hours
    
    # Export to ONNX
    torch.onnx.export(model,                     
                     (dummy_profiles, dummy_prices),  
                     output_path,                  
                     export_params=True,         
                     opset_version=12,           
                     do_constant_folding=True,   
                     input_names=['profiles', 'prices'],   
                     output_names=['actions'],    
                     dynamic_axes={'profiles': {0: 'batch_size'},    
                                 'prices': {0: 'batch_size'},
                                 'actions': {0: 'batch_size'}})
    
    print(f"Model converted and saved to {output_path}")
    
    # Test the converted model
    try:
        import onnx
        onnx_model = onnx.load(output_path)
        onnx.checker.check_model(onnx_model)
        print("ONNX model is valid!")
        
        import onnxruntime
        session = onnxruntime.InferenceSession(output_path)
        
        # Run test inference
        input_feed = {
            'profiles': dummy_profiles.numpy(),
            'prices': dummy_prices.numpy()
        }
        output = session.run(['actions'], input_feed)
        print(f"Test inference successful! Output shape: {output[0].shape}")
        
    except Exception as e:
        print(f"Error testing the model: {str(e)}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, 'energy_model.pth')
    convert_to_onnx(model_path)
