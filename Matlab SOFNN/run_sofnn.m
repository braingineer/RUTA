net = train_sofnn(trainX, trainY);

%%
disp('Training data...');
pred = test_sofnn(net, trainX, trainY);
fprintf('MAPE: %f SMAPE: %f\n', mape(trainY, pred), smape(trainY, pred));
figure;
plot(1:size(trainX,1), trainY,'b*');
hold on;
plot(1:size(trainX,1), pred,'r');

disp('Testing data...');
pred = test_sofnn(net, testX, testY);
fprintf('MAPE: %f SMAPE: %f\n', mape(testY, pred), smape(testY, pred));
figure;
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), pred,'r');