%% PREPROCESS
load DJIA_OF;

% size of training data
tsize = 117; % from visual inspection, corresponding to days preceding Dec

% clean OF data
% OF_C_NW_N = weed_of(OF_C_NW_N, DJIA);
% OF_C_W_N = weed_of(OF_C_W_N,DJIA);
% OF_NC_NW_N = weed_of(OF_NC_NW_N,DJIA);
% OF_NC_W_N = weed_of(OF_NC_W_N,DJIA);
% OF_C_NW_NN = weed_of(OF_C_NW_NN, DJIA);
% OF_C_W_NN = weed_of(OF_C_W_NN,DJIA);
% OF_NC_NW_NN = weed_of(OF_NC_NW_NN,DJIA);
% OF_NC_W_NN = weed_of(OF_NC_W_NN,DJIA);

% choose OF
% OF = OF_NC_W_N;

% inverting OF sentiment ratio
% OF(:,end) = 1./OF(:,end);
% OF_PP(:,end) = 1./OF_PP(:,end);

% smoothen sentiment ratios
% OF = smoothen_of(OF, size(OF,2), 7);
%OF_PP = smoothen_of(OF, size(OF_PP,2), 7);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% find optimal number of days
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
bestDay = 0;
bestSmape = 1000;
dayVals = [];
for i=1:10
    i0 = get_baseline(DJIA,i);
    i0 = scale(i0);
    
    [mapeval, smapeval] = ...
            regressEval(i0(1:tsize-1, 2:end-1), i0(1:tsize-1, end), ...
                i0(tsize:end, 2:end-1), i0(tsize:end, end));
    
    if smapeval < bestSmape
        bestSmape = smapeval;
        bestDay = i;
    end
    %fprintf('day: %d, mape: %f, smape: %f\n', i, mapeval, smapeval); 
    dayVals = [dayVals; [mapeval, smapeval]];
end

for i=1:10
    fprintf('day: %d, mape: %f, smape: %f\n', i, dayVals(i,1), dayVals(i,2)); 
end
fprintf('best day: %d, mape: %f, smape: %f\n', bestDay, dayVals(bestDay,1), bestSmape); 

% generate model matrices
%i0  = get_baseline(DJIA, 5);
% iOF = get_OFModel(DJIA, OF, 5);

% scale features to be between [0, 1]. Bollen et al (2010) say that makes
% every input be treated with similar importance.
%i0 = scale(i0);
% iOF = scale(iOF);
%iOF_PP = scale(iOF_PP);

bestDay = 0;
bestAcc = 0;
dayVals = [];
for i=1:10
    i0 = direction_data(get_baseline(DJIA,i));
    i0 = scale(i0);
    
    acc = classEval(i0(1:tsize-1, 2:end-1), i0(1:tsize-1, end), ...
                i0(tsize:end, 2:end-1), i0(tsize:end, end));
    
    if acc > bestAcc
        bestAcc = acc;
        bestDay = i;
    end
    %fprintf('day: %d, mape: %f, smape: %f\n', i, mapeval, smapeval); 
    dayVals = [dayVals; acc];
end

for i=1:10
    fprintf('day: %d, accuracy: %f\n', i, dayVals(i)); 
end
fprintf('best day: %d, accuracy: %f\n', bestDay, dayVals(bestDay)); 

%dir_i0 = direction_data(i0, 4);
% dir_iOF = direction_data(iOF, 4);

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
