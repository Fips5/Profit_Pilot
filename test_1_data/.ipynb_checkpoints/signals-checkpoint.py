      Non-trainable params\n",
      "66.9 K    Total params\n",
      "0.268     Total estimated model params size (MB)\n",
      "692       Modules in train mode\n",
      "0         Modules in eval mode\n"
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "6020faf0005441fb905785ed86d49fac",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Training: |                                                                                      | 0/? [00:00<…"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "`Trainer.fit` stopped: `max_epochs=8` reached.\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n",
      "C:\\Users\\david\\AppData\\Local\\anaconda3\\envs\\tws_env\\lib\\site-packages\\pandas\\core\\arraylike.py:399: RuntimeWarning: invalid value encountered in maximum\n",
      "  result = getattr(ufunc, method)(*inputs, **kwargs)\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "               timestamp     open     high      low    close volume\n",
      "995  2025-01-16 13:05:00    11.18    11.22    11.17    11.22  631.0\n",
      "996  2025-01-16 13:20:00  11.2119  11.2119  11.2119  11.2119  235.0\n",
      "997  2025-01-16 13:50:00    11.24    11.24    11.24    11.24  369.0\n",
      "998  2025-01-16 14:10:00   11.225   11.225   11.225   11.225  365.0\n",
      "999  2025-01-16 14:25:00    11.22    11.22    11.22    11.22  541.0\n",
      "step 1\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "GPU available: False, used: False\n",
      "TPU available: False, using: 0 TPU cores\n",
      "HPU available: False, using: 0 HPUs\n"
     ]
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "f895bb0982884d86800b3a16b794b21d",
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
      "C:\\Users\\david\\AppData\\Local\\Temp\\ipykernel_16240\\223882070.py:159: FutureWarning: The default fill_method='pad' in Series.pct_change is deprecated and will be removed in a future vers