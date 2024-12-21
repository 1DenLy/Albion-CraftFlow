import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import KFold
from matplotlib import pyplot as plt

# Примерные данные
prices_avg = [2792, 2835, 2776, 2703, 2740, 2785, 2777, 2764, 2744, 2726, 2717, 2694, 2554, 2443, 2399, 2441, 2426, 2459, 2544, 2467, 2303, 2269, 2230, 2148, 2294, 2554, 2413, 2691, 2863, 3025, 3008, 2962, 3050, 3211, 3295, 3312, 3352, 3333, 3248, 3235, 3247, 3254, 3209, 2975, 2887, 2960, 2932, 2964, 2941, 2940, 2918, 2946, 2925, 2957, 2954, 2961, 2943, 2970, 2939, 2954, 2542, 2896, 2904, 2812, 2772, 2752, 2760, 2731, 2730, 2709, 2699, 2634, 2662, 2650, 2656, 2585, 2583, 2565, 2565, 2525, 2523, 2565, 2561, 2528, 2564, 2568, 2547, 2562, 2563, 2635, 2593, 2737, 2764, 2798, 2840, 2697, 2904, 3009, 3084, 3117, 3070, 2964, 2674, 3791, 4378, 3341, 2815, 2897, 2858, 2868, 2889, 2905, 2920, 2850, 2889, 2874, 2900, 2847, 2885, 2863, 2865, 2916]

# Нормализация данных
scaler = MinMaxScaler()
prices_scaled = scaler.fit_transform(np.array(prices_avg).reshape(-1, 1))

# Создание временных окон
def create_dataset(dataset, time_step=1):
    dataX, dataY = [], []
    for i in range(len(dataset) - time_step):
        a = dataset[i:(i + time_step), 0]
        dataX.append(a)
        if i + time_step < len(dataset):
            dataY.append(dataset[i + time_step, 0])
    return np.array(dataX), np.array(dataY)

time_step = 10
X, y = create_dataset(prices_scaled, time_step)

# Изменение формы данных для LSTM [samples, time steps, features]
X = X.reshape(X.shape[0], X.shape[1], 1)

def create_model():
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.LSTM(units=50, return_sequences=True, input_shape=(time_step, 1)))
    model.add(tf.keras.layers.LSTM(units=50, return_sequences=False))
    model.add(tf.keras.layers.Dense(units=25))
    model.add(tf.keras.layers.Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# K-fold Cross Validation
kfold = KFold(n_splits=5, shuffle=True)
val_losses = []

for train_index, val_index in kfold.split(X):
    X_train, X_val = X[train_index], X[val_index]
    y_train, y_val = y[train_index], y[val_index]

    model = create_model()
    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    history = model.fit(X_train, y_train, validation_data=(X_val, y_val), batch_size=1, epochs=100, callbacks=[early_stopping], verbose=0)

    val_loss = model.evaluate(X_val, y_val, verbose=0)
    val_losses.append(val_loss)

# Средняя ошибка валидации
average_val_loss = np.mean(val_losses)
print(f"Average Validation Loss: {average_val_loss}")

# Обучение на всех данных с количеством эпох, найденным в результате K-fold Cross Validation
model = create_model()
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
history = model.fit(X, y, batch_size=1, epochs=100, callbacks=[early_stopping])

# Предсказание на будущее
future_steps = 24
last_known_data = prices_scaled[-time_step:]
future_predictions = []

for _ in range(future_steps):
    next_pred = model.predict(last_known_data.reshape(1, time_step, 1))
    future_predictions.append(next_pred[0, 0])
    last_known_data = np.append(last_known_data[1:], next_pred, axis=0)

# Обратное преобразование будущих предсказанных значений
future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

# Построение графика будущих предсказаний
plt.figure(figsize=(12, 6))
plt.plot(range(len(prices_avg)), scaler.inverse_transform(prices_scaled), label='Real Prices')
plt.plot(range(len(prices_avg), len(prices_avg) + future_steps), future_predictions, label='Future Predictions', linestyle='dashed')
plt.legend()
plt.show()
