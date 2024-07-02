authorised_capital = 200000
share_price = 100
current_shares = authorised_capital/share_price

equity_to_give = 5
money_to_give = 800000
new_valuation = (money_to_give/equity_to_give)*100

increased_shares = new_valuation/share_price
shares_to_give = increased_shares*(equity_to_give/100)

print(f"new valuation = {new_valuation}, shares to give = {shares_to_give}, total shares = {increased_shares}")