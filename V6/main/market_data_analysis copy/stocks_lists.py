def get_top_stocks(lists):
    # Technology
    tech_stocks = [
        "AAPL",  # Apple Inc.
        "MSFT",  # Microsoft Corporation
        "GOOGL", # Alphabet Inc. (Google)
        "AMZN",  # Amazon.com, Inc.
        "NVDA"   # NVIDIA Corporation
    ]
    
    # Healthcare
    healthcare_stocks = [
        "PFE",   # Pfizer Inc.
        "JNJ",   # Johnson & Johnson
        "MRNA",  # Moderna, Inc.
        "ABBV",  # AbbVie Inc.
        "BMY"    # Bristol-Myers Squibb Company
    ]
    
    # Financials
    financials_stocks = [
        "JPM",   # JPMorgan Chase & Co.
        "BAC",   # Bank of America Corporation
        "WFC",   # Wells Fargo & Co.
        "C",     # Citigroup Inc.
        "GS"     # Goldman Sachs Group, Inc.
    ]
    
    # Consumer Discretionary
    consumer_discretionary_stocks = [
        "TSLA",  # Tesla, Inc.
        "HD",    # Home Depot, Inc.
        "NKE",   # Nike, Inc.
        "DIS",   # The Walt Disney Company
        "MCD"    # McDonald's Corporation
    ]
    
    # Energy
    energy_stocks = [
        "XOM",   # Exxon Mobil Corporation
        "CVX",   # Chevron Corporation
        "BP",    # BP p.l.c.
        "TOT",   # TotalEnergies SE
        "EOG"    # EOG Resources, Inc.
    ]
    if lists == 'Top5/Industrys':
        return {
            "Technology": tech_stocks,
            "Healthcare": healthcare_stocks,
            "Financials": financials_stocks,
            "Consumer Discretionary": consumer_discretionary_stocks,
            "Energy": energy_stocks
        }
    if lists == 'main':
        main_list = [
            # Technology
            "AAPL",  # Apple Inc.
            "MSFT",  # Microsoft Corporation
            "GOOGL", # Alphabet Inc. (Google)
            "AMZN",  # Amazon.com, Inc.
            "NVDA",  # NVIDIA Corporation

            # Healthcare
            "PFE",   # Pfizer Inc.
            "JNJ",   # Johnson & Johnson
            "MRNA",  # Moderna, Inc.
            "ABBV",  # AbbVie Inc.
            "BMY",   # Bristol-Myers Squibb Company

            # Financials
            "JPM",   # JPMorgan Chase & Co.
            "BAC",   # Bank of America Corporation
            "WFC",   # Wells Fargo & Co.
            "C",     # Citigroup Inc.
            "GS",    # Goldman Sachs Group, Inc.

            # Consumer Discretionary
            "TSLA",  # Tesla, Inc.
            "HD",    # Home Depot, Inc.
            "NKE",   # Nike, Inc.
            "DIS",   # The Walt Disney Company
            "MCD",   # McDonald's Corporation

            # Energy
            "XOM",   # Exxon Mobil Corporation
            "CVX",   # Chevron Corporation
            "BP",    # BP p.l.c.
            "TOT",   # TotalEnergies SE
            "EOG"    # EOG Resources, Inc.
        ]

    
        return main_list
    else:
        reminder_msg = 'put in the function: main - for all stock, Top5/Industrys - for a categorized touple'
                                    
        return reminder_msg

