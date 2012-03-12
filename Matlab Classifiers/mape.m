function m = mape( A, F )
%MAPE Mean Absolute Percentage Error
%   A = Prediction
%   F = Real value
    
    m = 0;
    for i=1:size(A, 1)
        m = m + abs((A(i) - F(i))/A(i));
    end
    
    m = m * 100/size(A,1);
end

