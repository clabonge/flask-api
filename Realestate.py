class RealEstateAnalyzer:
    def __init__(self):
        self.properties = []
        self.market_trend_factor = 0  # -1 (declining), 0 (stable), 1 (growing)

    def input_property_data(self):
        """Collect data for a single property"""
        property = {}
        print("\nEnter Property Details:")
        property['name'] = input("Property Name/ID: ")
        property['current_value'] = float(input("Current Property Value ($): "))
        property['purchase_price'] = float(input("Original Purchase Price ($): "))
        property['monthly_rent'] = float(input("Monthly Rental Income ($): "))
        property['monthly_expenses'] = float(input("Monthly Expenses (excluding mortgage) ($): "))
        property['years_owned'] = float(input("Years Owned: "))
        property['annual_appreciation'] = float(input("Expected Annual Appreciation Rate (%): ")) / 100
        property['holding_period'] = float(input("Planned Additional Holding Period (years): "))
        property['selling_costs'] = float(input("Estimated Selling Costs (% of value): ")) / 100
        
        # Mortgage details
        property['has_mortgage'] = input("Has mortgage? (y/n): ").lower() == 'y'
        if property['has_mortgage']:
            property['mortgage_balance'] = float(input("Current Mortgage Balance ($): "))
            property['monthly_mortgage'] = float(input("Monthly Mortgage Payment ($): "))
            property['interest_rate'] = float(input("Mortgage Interest Rate (%): ")) / 100
        
        # Tax details
        property['tax_rate'] = float(input("Capital Gains Tax Rate (%): ")) / 100
        property['annual_property_tax'] = float(input("Annual Property Tax ($): "))
        
        self.properties.append(property)

    def set_market_trend(self):
        """Set overall market trend"""
        trend = input("Current Market Trend (declining/stable/growing): ").lower()
        if trend.startswith('d'):
            self.market_trend_factor = -1
        elif trend.startswith('g'):
            self.market_trend_factor = 1
        else:
            self.market_trend_factor = 0

    def calculate_roi(self, property):
        """Calculate Return on Investment"""
        total_investment = property['purchase_price']
        monthly_net = property['monthly_rent'] - property['monthly_expenses']
        if property['has_mortgage']:
            monthly_net -= property['monthly_mortgage']
        net_annual_income = monthly_net * 12 - property['annual_property_tax']
        roi = (net_annual_income / total_investment) * 100
        return roi

    def calculate_future_value(self, property):
        """Calculate future value with market trend adjustment"""
        appreciation = property['annual_appreciation'] + (self.market_trend_factor * 0.01)
        future_value = property['current_value'] * ((1 + appreciation) ** property['holding_period'])
        return future_value

    def calculate_sell_now_profit(self, property):
        """Calculate profit if sold now with taxes"""
        selling_costs = property['current_value'] * property['selling_costs']
        gross_profit = property['current_value'] - property['purchase_price'] - selling_costs
        if property['has_mortgage']:
            gross_profit -= property['mortgage_balance']
        tax = max(0, gross_profit * property['tax_rate'])  # No tax on losses
        net_profit = gross_profit - tax
        return net_profit

    def calculate_hold_profit(self, property):
        """Calculate profit if held with mortgage and taxes"""
        future_value = self.calculate_future_value(property)
        selling_costs = future_value * property['selling_costs']
        
        monthly_net = property['monthly_rent'] - property['monthly_expenses']
        if property['has_mortgage']:
            monthly_net -= property['monthly_mortgage']
        
        future_rental_profit = (monthly_net * 12 - property['annual_property_tax']) * property['holding_period']
        gross_profit = future_value + future_rental_profit - property['purchase_price']
        
        if property['has_mortgage']:
            remaining_balance = property['mortgage_balance'] * (1 + property['interest_rate']) ** property['holding_period']
            gross_profit -= remaining_balance
        
        tax = max(0, (gross_profit - future_rental_profit) * property['tax_rate'])
        net_profit = gross_profit - tax - selling_costs
        return net_profit

    def calculate_risk_score(self, property):
        """Calculate risk score (0-100)"""
        risk = 0
        # High mortgage-to-value ratio increases risk
        if property['has_mortgage']:
            loan_to_value = property['mortgage_balance'] / property['current_value']
            risk += min(50, loan_to_value * 50)
        
        # Negative cash flow increases risk
        monthly_net = property['monthly_rent'] - property['monthly_expenses']
        if property['has_mortgage']:
            monthly_net -= property['monthly_mortgage']
        if monthly_net < 0:
            risk += 30
        
        # Declining market increases risk
        if self.market_trend_factor < 0:
            risk += 20
        
        return min(100, risk)

    def analyze_property(self, property):
        """Analyze a single property"""
        print(f"\n=== Analysis for {property['name']} ===")
        
        roi = self.calculate_roi(property)
        print(f"Current Annual ROI: {roi:.2f}%")
        
        monthly_net = property['monthly_rent'] - property['monthly_expenses']
        if property['has_mortgage']:
            monthly_net -= property['monthly_mortgage']
        print(f"Current Net Monthly Cash Flow: ${monthly_net:.2f}")
        
        sell_profit = self.calculate_sell_now_profit(property)
        print(f"\nSell Now Scenario:")
        print(f"Estimated Net Profit (after tax): ${sell_profit:.2f}")
        
        hold_profit = self.calculate_hold_profit(property)
        future_value = self.calculate_future_value(property)
        print(f"\nHold for {property['holding_period']} Years Scenario:")
        print(f"Projected Future Value: ${future_value:.2f}")
        print(f"Total Projected Net Profit: ${hold_profit:.2f}")
        
        risk_score = self.calculate_risk_score(property)
        print(f"\nRisk Assessment Score (0-100): {risk_score:.2f}")
        if risk_score > 75:
            print("Risk Level: High")
        elif risk_score > 50:
            print("Risk Level: Medium")
        else:
            print("Risk Level: Low")
        
        print("\nRecommendation:")
        if sell_profit > hold_profit and risk_score > 50:
            print("Consider selling due to higher immediate profit and risk factors.")
        elif hold_profit > sell_profit and risk_score < 75:
            print("Consider holding for potentially higher returns and acceptable risk.")
        else:
            print("Decision is close - weigh personal goals and market conditions.")

    def analyze_all_properties(self):
        """Analyze all properties"""
        if not self.properties:
            print("No properties to analyze!")
            return
        for property in self.properties:
            self.analyze_property(property)

def main():
    analyzer = RealEstateAnalyzer()
    print("Welcome to the Enhanced Real Estate Investment Analyzer")
    
    analyzer.set_market_trend()
    num_properties = int(input("How many properties to analyze? "))
    
    for _ in range(num_properties):
        analyzer.input_property_data()
    
    analyzer.analyze_all_properties()

if __name__ == "__main__":
    main() 
