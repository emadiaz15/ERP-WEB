import React from "react";
import Table from "@/components/common/Table";

const StockEventTable = ({ headers, rows, columnClasses, sentinelRow }) => (
    <Table headers={headers} rows={rows} columnClasses={columnClasses} footer={sentinelRow} />
);

export default StockEventTable;