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
    <header className="sticky top-0 w-full z-40 bg-black/80 backdrop-blur-lg border-b border-cyan-500/20">
      <div className="container mx-auto flex items-center justify-between gap-2 p-4">
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(-1)}
            aria-label="Go back"
            className="border-gray-700 text-gray-300 hover:bg-gray-800 hover:text-white"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate("/")}
            aria-label="Go home"
            className="border-gray-700 text-gray-300 hover:bg-gray-800 hover:text-white"
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
                className={location.pathname.includes('/ai-insights') || location.pathname.includes('/dashboard/executive-summary') 
                  ? "bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 text-white border-0" 
                  : "border-gray-700 text-gray-300 hover:bg-gray-800 hover:text-white"}
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
