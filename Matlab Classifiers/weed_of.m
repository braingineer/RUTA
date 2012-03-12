function newof = weed_of( ofmat, data )
%WEED_OF Removes days from OF matrix that are weekends
%   compares days in ofmat and data matrices, and removes those days from
%   ofmat that do not have a corresponding entry in data

    newof = zeros(size(data,1), size(ofmat,2));
    j = 1;
    for i = 1:size(data,1)
        if data(i,1) == ofmat(j,1)
            newof(i,:) = ofmat(j,:);
            j = j + 1;
        else
            j = j + 1;
            while data(i,1) ~= ofmat(j, 1)
                j = j + 1;
            end
            newof(i,:) = ofmat(j,:);
        end
    end
end

