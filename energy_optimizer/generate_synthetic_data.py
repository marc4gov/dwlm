# ... [previous imports and functions remain the same until main] ...

if __name__ == "__main__":
    # Set paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pump_dir = os.path.join(script_dir, "pump_profiles")
    
    if not os.path.exists(pump_dir):
        os.makedirs(pump_dir)
    
    # Generate synthetic data
    base_profile = os.path.join(pump_dir, "katwijk_profile.csv")
    num_days = 100
    
    try:
        profiles, prices = generate_training_data(num_days, base_profile)
        
        # Save synthetic data - without datum column
        
        # Save profiles
        profiles_df = pd.DataFrame(profiles, columns=[str(i) for i in range(24)])
        profiles_df.to_csv(os.path.join(pump_dir, 'synthetic_profiles.csv'), index=False)
        
        # Save prices
        prices_df = pd.DataFrame(prices, columns=[str(i) for i in range(24)])
        prices_df.to_csv(os.path.join(pump_dir, 'synthetic_prices.csv'), index=False)
        
        # Plot some samples
        fig = plot_synthetic_data(profiles, prices)
        plt.savefig(os.path.join(pump_dir, 'synthetic_data_samples.png'))
        
        print(f"Generated {num_days} days of synthetic data")
        print(f"Files saved in: {pump_dir}")
        print("- synthetic_profiles.csv")
        print("- synthetic_prices.csv")
        print("- synthetic_data_samples.png")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())