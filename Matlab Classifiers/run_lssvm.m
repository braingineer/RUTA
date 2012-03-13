%% PREPROCESS
load DJIA_OF;

% clean OF data
OF_C_NW_N = weed_of(OF_C_NW_N, DJIA);
OF_C_W_N = weed_of(OF_C_W_N,DJIA);
OF_NC_NW_N = weed_of(OF_NC_NW_N,DJIA);
OF_NC_W_N = weed_of(OF_NC_W_N,DJIA);
OF_C_NW_NN = weed_of(OF_C_NW_NN, DJIA);
OF_C_W_NN = weed_of(OF_C_W_NN,DJIA);
OF_NC_NW_NN = weed_of(OF_NC_NW_NN,DJIA);
OF_NC_W_NN = weed_of(OF_NC_W_NN,DJIA);

% choose OF
OF = OF_NC_W_N;

% inverting OF sentiment ratio
% OF(:,end) = 1./OF(:,end);
% OF_PP(:,end) = 1./OF_PP(:,end);

% smoothen sentiment ratios
OF = smoothen_of(OF, size(OF,2), 7);
%OF_PP = smoothen_of(OF, size(OF_PP,2), 7);

% generate model matrices
i0  = get_baseline(DJIA);
iOF = get_OFModel(DJIA, OF);
%iOF_PP = get_OFModel(DJIA, OF_PP);

% scale features to be between [0, 1]. Bollen et al (2010) say that makes
% every input be treated with similar importance.
i0 = scale(i0);
iOF = scale(iOF);
%iOF_PP = scale(iOF_PP);

% size of training data
tsize = 117; % from visual inspection, corresponding to days preceding Dec

dir_i0 = direction_data(i0, 4);
dir_iOF = direction_data(iOF, 4);
%dir_iOF_PP = direction_data(iOF_PP, 4);

%% VISUALIZING DATA
figure;
startDate = datenum('2009-06-11');
endDate   = datenum('2009-12-31');
xData = linspace(startDate, endDate, 142);

scDJIA = scale(DJIA);
scOF_C_NW_N = scale(OF_C_NW_N);
scOF_C_W_N = scale(OF_C_W_N);
scOF_NC_NW_N = scale(OF_NC_NW_N);
scOF_NC_W_N = scale(OF_NC_W_N);
scOF_C_NW_NN = scale(OF_C_NW_NN);
scOF_C_W_NN = scale(OF_C_W_NN);
scOF_NC_NW_NN = scale(OF_NC_NW_NN);
scOF_NC_W_NN = scale(OF_NC_W_NN);
%scOF_PP = scale(OF_PP);

plot(xData, scDJIA(:,2),  ...
    xData, scOF_C_NW_N(:,4), xData, scOF_C_W_N(:,4),...
    xData, scOF_NC_NW_N(:,4), xData, scOF_NC_W_N(:,4), ...
    xData, scOF_C_NW_NN(:,4), xData, scOF_C_W_NN(:,4),...
    xData, scOF_NC_NW_NN(:,4), xData, scOF_NC_W_NN(:,4));
ylim([-.5 2]);
grid on;
set(gca, 'XTick', xData);
hold on;
% 
% plot(xData, scOF_C_NW_NN(:,4));
% plot(xData, scOF_C_W_NN(:,4));
% plot(xData, scOF_NC_NW_NN(:,4));
% plot(xData, scOF_NC_W_NN(:,4));
%plot(xData, scOF_PP(:,4), 'g');

yL = get(gca, 'YLim');
line([xData(1) xData(1)], yL, 'Color', 'k');
text(xData(2), 1.25, '06/11/2009');

line([xData(end) xData(end)], yL, 'Color', 'k');
text(xData(end-9), 1.25, '12/31/2009');
%annotation('textarrow', [xData(1), xData(3)], [.9 .9], 'String', '06/16/2009');

datetick('x', 'mmm');
legend('DJIA','C-NoWt-Neu', 'C-Wt-Neu', 'NoC-NoWt-Neu', 'NoC-Wt-Neu',... 
    'C-NoWt-NoNeu', 'C-Wt-NoNeu', 'NoC-NoWt-NoNeu', 'NoC-Wt-NoNeu');

%% SCALE AND SEE POSITIVE Vs. NEGATIVE SENTIMENT NUMBERS
figure;
%subplot(1,2,1);
startDate = datenum('2009-06-11');
endDate   = datenum('2009-12-31');
xData = linspace(startDate, endDate, 142);

plot(xData, scOF(:,2));
ylim([-.5 2]);
grid on;
set(gca, 'XTick', xData);
hold on;
plot(xData, scOF(:,3), 'r');

%annotation('textarrow', [xData(1), xData(3)], [.9 .9], 'String', '06/16/2009');

datetick('x', 'mmm');
title('OF unprocessed');
legend('positive', 'negative');

% subplot(1,2,2);
% startDate = datenum('2009-06-11');
% endDate   = datenum('2009-12-31');
% xData = linspace(startDate, endDate, 142);
% 
% plot(xData, scOF_PP(:,2));
% ylim([-.5 2]);
% grid on;
% set(gca, 'XTick', xData);
% hold on;
% plot(xData, scOF_PP(:,3), 'r');
% %annotation('textarrow', [xData(1), xData(3)], [.9 .9], 'String', '06/16/2009');
% 
% datetick('x', 'mmm');
% title('OF preprocessed');
% legend('positive', 'negative');

%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EXACT PREDICTION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% BASELINE -- ONLY DJIA DATA

disp(' ');
disp('DJIA Data only');
% MAKE MODEL
type = 'function estimation';
X = i0(1:tsize-1, 2:end-1);
Y = i0(1:tsize-1, end);
testX = i0(tsize:end, 2:end-1);
testY = i0(tsize:end, end);
kernel = 'RBF_kernel';
gam = 2;
sig2 = .8;

% RUN AND TEST
model = initlssvm(X,Y,type,gam,sig2,kernel);
model = trainlssvm(model);
Yp = simlssvm(model, X);
disp(' ');
disp('Training data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, Y), smape(Yp, Y));
plotlssvm(model);

Yp = simlssvm(model, testX);
disp(' ');
disp('Testing data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, testY), smape(Yp, testY));
figure;
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), Yp,'r');

%% DJIA DATA WITH OF

disp(' ');
disp('DJIA Data with OF');
% MAKE MODEL
type = 'function estimation';
X = iOF(1:tsize-1, 2:end-1);
Y = iOF(1:tsize-1, end);
testX = iOF(tsize:end, 2:end-1);
testY = iOF(tsize:end, end);
kernel = 'RBF_kernel';
gam = 2;
sig2 = .8;

%RUN AND TEST
model = initlssvm(X,Y,type,gam,sig2,kernel);
model = trainlssvm(model);
Yp = simlssvm(model, X);
disp(' ');
disp('Training data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, Y), smape(Yp, Y));
plotlssvm(model);

Yp = simlssvm(model, testX);
disp(' ');
disp('Testing data...');
fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, testY), smape(Yp, testY));
figure;
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), Yp,'r');

%% DJIA DATA WITH PRE-PROCESSED OF
% 
% disp(' ');
% disp('DJIA Data with Pre-Processed OF');
% % MAKE MODEL
% type = 'function estimation';
% X = iOF_PP(1:tsize-1, 2:end-1);
% Y = iOF_PP(1:tsize-1, end);
% testX = iOF_PP(tsize:end, 2:end-1);
% testY = iOF_PP(tsize:end, end);
% kernel = 'RBF_kernel';
% gam = 5;
% sig2 = .8;
% 
% % RUN AND TEST
% model = initlssvm(X,Y,type,gam,sig2,kernel);
% model = trainlssvm(model);
% Yp = simlssvm(model, X);
% disp(' ');
% disp('Training data...');
% fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, Y), smape(Yp, Y));
% plotlssvm(model);
% 
% Yp = simlssvm(model, testX);
% disp(' ');
% disp('Testing data...');
% fprintf('MAPE: %f SMAPE: %f\n', mape(Yp, testY), smape(Yp, testY));
% figure;
% plot(1:size(testX,1), testY,'b*');
% hold on;
% plot(1:size(testX,1), Yp,'r');

%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% DIRECTION TESTING
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% BASELINE -- DJIA DATA ONLY

disp(' ');
disp('Direction testing w/ DJIA Data only');

type = 'classification';
X = dir_i0(1:tsize-1, 2:end-1);
Y = dir_i0(1:tsize-1, end);
testX = dir_i0(tsize:end, 2:end-1);
testY = dir_i0(tsize:end, end);
kernel = 'RBF_kernel';
gam = 2;
sig2 = .8;

% RUN AND TEST
model = initlssvm(X,Y,type,gam,sig2,kernel);
model = trainlssvm(model);
Yp = simlssvm(model, X);
disp(' ');
disp('Training data...');
fprintf('Accuracy: %f\n', sum(Yp == Y)/size(Yp,1));
figure;
subplot(1,2,1);
plot(1:size(X,1), Y,'b*');
hold on;
plot(1:size(X,1), Yp,'r.');
ylim([-1 2]);
%plotlssvm(model);

Yp = simlssvm(model, testX);
disp(' ');
disp('Testing data...');
fprintf('Accuracy: %f\n', sum(Yp == testY)/size(Yp,1));
subplot(1,2,2);
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), Yp,'r.');
ylim([-1 2]);

%% DJIA DATA W/ UNPROCESSED OF

disp(' ');
disp('Direction testing w/ DJIA & OF data');

type = 'classification';
X = dir_iOF(1:tsize-1, 2:end-1);
Y = dir_iOF(1:tsize-1, end);
testX = dir_iOF(tsize:end, 2:end-1);
testY = dir_iOF(tsize:end, end);
kernel = 'RBF_kernel';
gam = 10;
sig2 = .8;

% RUN AND TEST
model = initlssvm(X,Y,type,gam,sig2,kernel);
model = trainlssvm(model);
Yp = simlssvm(model, X);
disp(' ');
disp('Training data...');
fprintf('Accuracy: %f\n', sum(Yp == Y)/size(Yp,1));
figure;
subplot(1,2,1);
plot(1:size(X,1), Y,'b*');
hold on;
plot(1:size(X,1), Yp,'r.');
ylim([-1 2]);
%plotlssvm(model);

Yp = simlssvm(model, testX);
disp(' ');
disp('Testing data...');
fprintf('Accuracy: %f\n', sum(Yp == testY)/size(Yp,1));
subplot(1,2,2);
plot(1:size(testX,1), testY,'b*');
hold on;
plot(1:size(testX,1), Yp,'r.');
ylim([-1 2]);

%% DJIA DATA W/ PRE-PROCESSED OF
% 
% disp(' ');
% disp('Direction testing w/ DJIA & pre-processed OF data');
% 
% type = 'classification';
% X = dir_iOF_PP(1:tsize-1, 2:end-1);
% Y = dir_iOF_PP(1:tsize-1, end);
% testX = dir_iOF_PP(tsize:end, 2:end-1);
% testY = dir_iOF_PP(tsize:end, end);
% kernel = 'RBF_kernel';
% gam = 10;
% sig2 = .8;
% 
% % RUN AND TEST
% model = initlssvm(X,Y,type,gam,sig2,kernel);
% model = trainlssvm(model);
% Yp = simlssvm(model, X);
% disp(' ');
% disp('Training data...');
% fprintf('Accuracy: %f\n', sum(Yp == Y)/size(Yp,1));
% figure;
% subplot(1,2,1);
% plot(1:size(X,1), Y,'b*');
% hold on;
% plot(1:size(X,1), Yp,'r.');
% ylim([-1 2]);
% %plotlssvm(model);
% 
% Yp = simlssvm(model, testX);
% disp(' ');
% disp('Testing data...');
% fprintf('Accuracy: %f\n', sum(Yp == testY)/size(Yp,1));
% subplot(1,2,2);
% plot(1:size(testX,1), testY,'b*');
% hold on;
% plot(1:size(testX,1), Yp,'r.');
% ylim([-1 2]);