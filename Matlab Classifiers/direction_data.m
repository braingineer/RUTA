function dirdata = direction_data( data, pday_c )
%DIRECTION_DATA generates binary direction data
%   data = data matrix with last column as the day's value
%   pday_c = column index of the value corresponding to the prev day

    dirdata = data;
    
    dirdata(:,end) = (data(:,end) > data(:,pday_c));
end

