import React, { useEffect, useState } from "react";
import { useAssessment } from "../contexts/AssessmentContext";
import { useAuth } from "../contexts/AuthContext";
import { Input } from "@/components/ui/input.jsx";
import { Label } from "@/components/ui/label.jsx";
import { Button } from "@/components/ui/button.jsx";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card.jsx";

const ProfileSettings = () => {
  const { userProfile, updateProfile } = useAssessment();
  const { user, apiService } = useAuth();
  const [status, setStatus] = useState("");
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    age: "",
    location: "",
    currentRole: "",
    experience: "",
  });

  useEffect(() => {
    setFormData({
      firstName: userProfile.firstName || "",
      lastName: userProfile.lastName || "",
      email: user?.email || userProfile.email || "",
      age: userProfile.age || "",
      location: userProfile.location || "",
      currentRole: userProfile.currentRole || "",
      experience: userProfile.experience || "",
    });
  }, [userProfile, user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    updateProfile(formData);
    try {
      await apiService.updateEntrepreneurProfile(formData);
      setStatus("Profile updated successfully");
    } catch {
      setStatus("Failed to update profile");
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>Profile Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="firstName">First Name</Label>
                <Input
                  id="firstName"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                />
              </div>
              <div>
                <Label htmlFor="lastName">Last Name</Label>
                <Input
                  id="lastName"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="age">Age</Label>
                <Input
                  id="age"
                  name="age"
                  value={formData.age}
                  onChange={handleChange}
                />
              </div>
              <div>
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="currentRole">Current Role</Label>
              <Input
                id="currentRole"
                name="currentRole"
                value={formData.currentRole}
                onChange={handleChange}
              />
            </div>
            <div>
              <Label htmlFor="experience">Years of Experience</Label>
              <Input
                id="experience"
                name="experience"
                value={formData.experience}
                onChange={handleChange}
              />
            </div>
            {status && <p className="text-sm text-green-400">{status}</p>}
            <Button type="submit" className="mt-4">
              Save Changes
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProfileSettings;
