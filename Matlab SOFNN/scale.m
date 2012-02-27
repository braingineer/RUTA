function scaledData = scale( data )
    [rows,cols] = size(data);

    scaledData    = zeros(rows,cols);

    maxData = max(data);
    minData = min(data);

    for c = 1:cols
        scaledData(:,c) = (data(:,c) - minData(c)) ./ (maxData(c) - minData(c));
    end

end

