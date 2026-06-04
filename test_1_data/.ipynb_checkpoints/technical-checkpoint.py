naconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "GPU available: False, used: False\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "                    0        1        2        3        4\n",
      "forecast_values  13.9  13.8861  13.8722  13.8583  13.8444\n",
      "step 2\n",
      "               timestamp   open    high    low    close  volume\n",
      "995  2025-01-17 14:30:00  10.88   10.88  10.88    10.88   131.0\n",
      "996  2025-01-17 14:50:00  10.88   10.88  10.88    10.88   254.0\n",
      "997  2025-01-17 14:55:00  10.87   10.87  10.82    10.82  1601.0\n",
      "998  2025-01-17 15:00:00   10.8    10.8   10.8     10.8   665.0\n",
      "999  2025-01-17 15:25:00   10.8  10.875   10.8  10.8105  1023.0\n",
      "step 1\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "TPU available: False, using: 0 TPU cores\n",
      "HPU available: False, using: 0 HPUs\n"
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "e214bee667ad4ab789c5301e244d4334",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Predicting: |                                                                                    | 0/? [00:00<…"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\david\\AppData\\Local\\Temp\\ipykernel_16240\\223882070.py:159: FutureWarning: The default fill_method='pad' in Series.pct_change is deprecated and will be removed in a future version. Either fill in any non-leading NA values prior to calling pct_change or specify 'fill_method=None' to not fill NA values.\n",
      "  forecast_pct = pd.Series(forecast_values).pct_change().fillna(0).cumsum() #forecasted value\n",
      "C:\\Users\\david\\AppData\\Local\\Temp\\ipykernel_16240\\223882070.py:160: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`\n",
      "  real_pct = n_df['close'].pct_change().fillna(0).cumsum()\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "GPU available: False, used: False\n",
      "TPU available: False, using: 0 TPU cores\n",
      "HPU available: False, using: 0 HPUs\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "                    0        1        2        3        4\n",
      "forecast_values  13.9  13.8861  13.8722  13.8583  13.8444\n",
      "step 2\n",
      "               timestamp   open    high    low    close  volume\n",
      "995  2025-01-17 14:50:00  10.88   10.88  10.88    10.88   254.0\n",
      "996  2025-01-17 14:55:00  10.87   10.87  10.82    10.82  1601.0\n",
      "997  2025-01-17 15:00:00   10.8    10.8   10.8     10.8   665.0\n",
      "998  2025-01-17 15:25:00   10.8  10.875   10.8  10.8105  1023.0\n",
      "999  2025-01-17 15:30:00   10.8    10.8   10.8     10.8   141.0\n",
      "step 1\n"
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "805744a085b94b44af18f780c7b6c610",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Predicting: |                                                                                    | 0/? [00:00<…"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\david\\AppData\\Local\\Temp\\ipykernel_16240\\223882070.py:159: FutureWarning: The default fill_method='pad' in Series.pct_change is deprecated and will be removed in a future version. Either fill in any non-leading NA values prior to calling pct_change or specify 'fill_method=None' to not fill NA values.\n",
      "  forecast_pct = pd.Series(forecast_values).pct_change().fillna(0).cumsum() #forecasted value\n",
      "C:\\Users\\david\\AppData\\Local\\Temp\\ipykernel_16240\\223882070.py:160: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`\n",
      "  real_pct = n_df['close'].pct_change().fillna(0).cumsum()\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "GPU available: False, used: False\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "                    0        1        2        3        4\n",
      "forecast_values  13.9  13.8861  13.8722  13.8583  13.8444\n",
      "step 2\n",
      "               timestamp   open    high    low    close  volume\n",
      "995  2025-01-17 14:55:00  10.87   10.87  10.82    10.82  1601.0\n",
      "996  2025-01-17 15:00:00   10.8    10.8   10.8     10.8   665.0\n",
      "997  2025-01-17 15:25:00   10.8  10.875   10.8  10.8105  1023.0\n",
      "998  2025-01-17 15:30:00   10.8    10.8   10.8     10.8   141.0\n",
      "999  2025-01-17 15:40:00  10.81   10.81  10.81    10.81   100.0\n",
      "step 1\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "TPU available: False, using: 0 TPU cores\n",
      "HPU available: False, using: 0 HPUs\n"
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "45c27967b6ce4180b2689ffac603c06e",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Predicting: |                                                                                    | 0/? [00:00<…"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\david\\AppData\\Local\\Temp\\ipykernel_16240\\223882070.py:159: FutureWarning: The default fill_method='pad' in Series.pct_change is deprecated and will be removed in a future version. Either fill in any non-leading NA values prior to calling pct_change or specify 'fill_method=None' to not fill NA values.\n",
      "  forecast_pct = pd.Series(forecast_values).pct_change().fillna(0).cumsum() #forecasted value\n",
      "C:\\Users\\david\\AppData\\Local\\Temp\\ipykernel_16240\\223882070.py:160: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`\n",
      "  real_pct = n_df['close'].pct_change().fillna(0).cumsum()\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "GPU available: False, used: False\n",
      "TPU available: False, using: 0 TPU cores\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "                    0        1        2        3        4\n",
      "forecast_values  13.9  13.8861  13.8722  13.8583  13.8444\n",
      "step 2\n",
      "               timestamp     open     high      low    close  volume\n",
      "995  2025-01-17 15:00:00     10.8     10.8     10.8     10.8   665.0\n",
      "996  2025-01-17 15:25:00     10.8   10.875     10.8  10.8105  1023.0\n",
      "997  2025-01-17 15:30:00     10.8     10.8     10.8     10.8   141.0\n",
      "998  2025-01-17 15:40:00    10.81    10.81    10.81    10.81   100.0\n",
      "999  2025-01-17 15:45:00  10.8001  10.8001  10.8001  10.8001   115.0\n",
      "step 1\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "HPU available: False, using: 0 HPUs\n"
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "ec546405eb4847db805bcde7986e77de",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Predicting: |                                                                                    | 0/? [00:00<…"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\david\\AppData\\Local\\Temp\\ipykernel_16240\\223882070.py:159: FutureWarning: The default fill_method='pad' in Series.pct_change is deprecated and will be removed in a future version. Either fill in any non-leading NA values prior to calling pct_change or specify 'fill_method=None' to not fill NA values.\n",
      "  forecast_pct = pd.Series(forecast_values).pct_change().fillna(0).cumsum() #forecasted value\n",
      "C:\\Users\\david\\AppData\\Local\\Temp\\ipykernel_16240\\223882070.py:160: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`\n",
      "  real_pct = n_df['close'].pct_change().fillna(0).cumsum()\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "GPU available: False, used: False\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "                    0        1        2        3        4\n",
      "forecast_values  13.9  13.8861  13.8722  13.8583  13.8444\n",
      "step 2\n",
      "               timestamp     open     high      low    close  volume\n",
      "995  2025-01-17 15:25:00     10.8   10.875     10.8  10.8105  1023.0\n",
      "996  2025-01-17 15:30:00     10.8     10.8     10.8     10.8   141.0\n",
      "997  2025-01-17 15:40:00    10.81    10.81    10.81    10.81   100.0\n",
      "998  2025-01-17 15:45:00  10.8001  10.8001  10.8001  10.8001   115.0\n",
      "999  2025-01-17 15:50:00   10.875    10.88  10.8072  10.8072  3069.0\n",
      "step 1\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "TPU available: False, using: 0 TPU cores\n",
      "HPU available: False, using: 0 HPUs\n"
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "1d37d8f2be334850a037da20a52041ee",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Predicting: |                                                                                    | 0/? [00:00<…"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\david\\AppData\\Local\\Temp\\ipykernel_16240\\223882070.py:159: FutureWarning: The default fill_method='pad' in Series.pct_change is deprecated and will be removed in a future version. Either fill in any non-leading NA values prior to calling pct_change or specify 'fill_method=None' to not fill NA values.\n",
      "  forecast_pct = pd.Series(forecast_values).pct_change().fillna(0).cumsum() #forecasted value\n",
      "C:\\Users\\david\\AppData\\Local\\Temp\\ipykernel_16240\\223882070.py:160: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`\n",
      "  real_pct = n_df['close'].pct_change().fillna(0).cumsum()\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "GPU available: False, used: False\n",
      "TPU available: False, using: 0 TPU cores\n",
      "HPU available: False, using: 0 HPUs\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "                    0        1        2        3        4\n",
      "forecast_values  13.9  13.8861  13.8722  13.8583  13.8444\n",
      "step 2\n",
      "               timestamp     open     high      low    close  volume\n",
      "995  2025-01-17 15:30:00     10.8     10.8     10.8     10.8   141.0\n",
      "996  2025-01-17 15:40:00    10.81    10.81    10.81    10.81   100.0\n",
      "997  2025-01-17 15:45:00  10.8001  10.8001  10.8001  10.8001   115.0\n",
      "998  2025-01-17 15:50:00   10.875    10.88  10.8072  10.8072  3069.0\n",
      "999  2025-01-17 15:55:00   10.835   10.835    10.81   10.835   824.0\n",
      "step 1\n"
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "8be3ef7b881e45bc92eb8679f7f3838f",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Predicting: |                                                                                    | 0/? [00:00<…"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\david\\AppData\\Local\\Temp\\ipykernel_16240\\223882070.py:159: FutureWarning: The default fill_method='pad' in Series.pct_change is deprecated and will be removed in a future version. Either fill in any non-leading NA values prior to calling pct_change or specify 'fill_method=None' to not fill NA values.\n",
      "  forecast_pct = pd.Series(forecast_values).pct_change().fillna(0).cumsum() #forecasted value\n",
      "C:\\Users\\david\\AppData\\Local\\Temp\\ipykernel_16240\\223882070.py:160: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`\n",
      "  real_pct = n_df['close'].pct_change().fillna(0).cumsum()\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: 