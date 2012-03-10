function iOF = get_OFModel( djia, ofmat )
%GET_OFMODEL returns OF model matrix
%   djia = matrix with daily closing values
%   ofmat = matrix with daily sentiment ratios as the last column
%   the function creates a feature/output matrix with the first column
%   containing the date, the next 3 columns containing the previous 3 days'
%   closing values, the further 3 columns containing the previous 3 days'
%   sentiment ratios, and the last column containing the closing value of
%   that day.

    iOF = zeros(size(djia,1)-3, 8);

    for i = 4:size(djia,1)
        iOF(i-3,:) = [djia(i,1) djia(i-3,2) djia(i-2,2) djia(i-1,2)...
              ofmat(i-3,end) ofmat(i-2,end) ofmat(i-1,end) djia(i,2)];
    end
end

