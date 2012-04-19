function iOF = get_OFModel( djia, ofmat, n )
%GET_OFMODEL returns OF model matrix
%   djia = matrix with daily closing values
%   ofmat = matrix with daily sentiment ratios as the last column
%   n = number of preceding days to use as features
%   the function creates a feature/output matrix with the first column
%   containing the date, the next n columns containing the previous n days'
%   closing values, the further n columns containing the previous n days'
%   sentiment ratios, and the last column containing the closing value of
%   that day.

    iOF = zeros(size(djia,1)-n, 2*n+2);

    for i = n+1:size(djia,1)
        temp = djia(i,1);
        for j = n:-1:1
            temp = [temp djia(i-j,2)];
        end
        
        for j = n:-1:1
            temp = [temp ofmat(i-j,end)];
        end
        
        temp = [temp djia(i,2)];
        
        iOF(i-n,:) = temp;
    end
end

