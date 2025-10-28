import React from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { Button } from "@/components/ui/button.jsx";
import { Brain, Home, ArrowLeft } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";

const NavBar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  if (location.pathname === "/") return null;

  return (
    <header className="sticky top-0 w-full z-40 bg-background/80 backdrop-blur border-b">
      <div className="container mx-auto flex items-center justify-between gap-2 p-4">
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(-1)}
            aria-label="Go back"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate("/")}
            aria-label="Go home"
          >
            <Home className="h-4 w-4 mr-2" />
            Home
          </Button>
        </div>
        
        {isAuthenticated && (
          <div className="flex gap-2">
            <Link to="/ai-insights">
              <Button
                variant={location.pathname.includes('/ai-insights') || location.pathname.includes('/dashboard/executive-summary') ? "default" : "outline"}
                size="sm"
              >
                <Brain className="h-4 w-4 mr-2" />
                AI Insights
              </Button>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};

export default NavBar;
