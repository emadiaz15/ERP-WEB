import React from "react";
import Toolbar from "@/components/common/Toolbar";
import { useNavigate } from "react-router-dom";

const StockEventToolbar = ({ title, buttonText, onButtonClick, backTo }) => {
    const navigate = useNavigate();
    return (
        <Toolbar
            title={title}
            buttonText={buttonText}
            onButtonClick={onButtonClick}
            onBackClick={() => navigate(backTo || -1)}
        />
    );
};

export default StockEventToolbar;