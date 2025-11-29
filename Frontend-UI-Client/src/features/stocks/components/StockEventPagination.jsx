import React from "react";
import Pagination from "@/components/ui/Pagination";

const StockEventPagination = ({ onNext, onPrevious, hasNext, hasPrevious }) => (
    <Pagination
        onNext={onNext}
        onPrevious={onPrevious}
        hasNext={hasNext}
        hasPrevious={hasPrevious}
    />
);

export default StockEventPagination;