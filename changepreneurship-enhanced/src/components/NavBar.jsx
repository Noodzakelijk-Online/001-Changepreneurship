import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button.jsx";

const NavBar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  if (location.pathname === "/") return null;

  return (
    <header className="sticky top-0 w-full z-40 bg-background/80 backdrop-blur">
      <div className="container mx-auto flex gap-2 p-4">
        <Button
          variant="outline"
          onClick={() => navigate(-1)}
          aria-label="Go back"
        >
          Back
        </Button>
        <Button
          variant="outline"
          onClick={() => navigate("/")}
          aria-label="Go home"
        >
          Home
        </Button>
      </div>
    </header>
  );
};

export default NavBar;
