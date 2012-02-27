function sm = smape( A, F )
%MAPE Symmetric Mean Absolute Percentage Error
%   Detailed explanation goes here -- Later!
    
    sm = 0;
    for i=1:size(A, 1)
        sm = sm + abs(A(i) - F(i))/(A(i) + F(i));
    end
    
    sm = sm /size(A,1);
end

