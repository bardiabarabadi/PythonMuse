function [filteredSample,pastSamples,pastResults] = biQuadFilter(coefficients,eegSample,pastSamples,pastResults)

    % function to apply a biQuad filter

    filteredSample = zeros(size(eegSample,1),size(eegSample,2));

    nPoints = size(eegSample,2);
    
    % note, this filter assumes that the last point is the oldest which is
    % why it is working backwards, in the case of this use it is because we
    % flip the plot data so oldest is at the last index and not index 1,
    % which is the opposite to how it is read

    for sampleCounter = nPoints:-1:1

        filteredSample(:,sampleCounter) = coefficients(1) * eegSample(:,sampleCounter) + coefficients(2) * pastSamples(:,1) + coefficients(3) * pastSamples(:,2) - coefficients(4) * pastResults(:,1) - coefficients(5) * pastResults(:,2);
        pastSamples(:,2) = pastSamples(:,1);
        pastSamples(:,1) = eegSample(:,sampleCounter);
        pastResults(:,2) = pastResults(:,1);
        pastResults(:,1) = filteredSample(:,sampleCounter);

    end

end