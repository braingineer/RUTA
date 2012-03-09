function sm = smape( A, F )
%MAPE Symmetric Mean Absolute Percentage Error
%   A = Prediction
%   F = Real value
    
    sm = 0;
    for i=1:size(A, 1)
        sm = sm + abs(A(i) - F(i))/(A(i) + F(i));
    end
    
    sm = sm * 100/size(A,1);
end

