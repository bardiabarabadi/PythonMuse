function [sample,samples,results] = applyBiQuad(sample,whichFilters,highPass,lowPass,notchFilter,samples,results)

    if whichFilters(1) == 1
        [sample,samples(:,:,1),results(:,:,1)] = biQuadFilter(highPass,sample,squeeze(samples(:,:,1)),squeeze(results(:,:,1)));
    end
    if whichFilters(2) == 1
        [sample,samples(:,:,2),results(:,:,2)] = biQuadFilter(lowPass,sample,squeeze(samples(:,:,2)),squeeze(results(:,:,2)));
    end
    if whichFilters(3) == 1
        [sample,samples(:,:,3),results(:,:,3)] = biQuadFilter(notchFilter,sample,squeeze(samples(:,:,3)),squeeze(results(:,:,3)));
    end

end