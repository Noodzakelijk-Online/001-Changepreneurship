import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
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
import { Upload, Sparkles, FileText, Shield, Link2, ChevronRight } from "lucide-react";

const ProfileSettings = () => {
  const { userProfile, updateProfile } = useAssessment();
  const { user, apiService } = useAuth();
  const [status, setStatus] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeStatus, setResumeStatus] = useState("");
  const [resumeLoading, setResumeLoading] = useState(false);
  const [resumeAnalysis, setResumeAnalysis] = useState(null);
  const [resumeData, setResumeData] = useState(null);
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

  useEffect(() => {
    let cancelled = false;

    const loadProfile = async () => {
      const result = await apiService.getProfile();
      if (!cancelled && result.success && result.data?.profile) {
        setResumeAnalysis(result.data.profile.resume_analysis || null);
        setResumeData(result.data.profile.resume_data || null);
      }
    };

    loadProfile();
    return () => {
      cancelled = true;
    };
  }, [apiService]);

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

  const handleResumeUpload = async () => {
    if (!resumeFile) {
      setResumeStatus("Choose a PDF or TXT resume first");
      return;
    }

    setResumeLoading(true);
    setResumeStatus("");
    try {
      const result = await apiService.uploadResume(resumeFile);
      if (!result.success) {
        setResumeStatus(result.error || "Failed to analyze resume");
        return;
      }

      setResumeData(result.data?.parsed_data || null);
      setResumeAnalysis(result.data?.analysis || null);

      const suggested = result.data?.suggested_profile || {};
      setFormData((prev) => ({
        ...prev,
        currentRole: suggested.currentRole || prev.currentRole,
        experience: suggested.experience || prev.experience,
      }));

      setResumeStatus("Resume analyzed successfully");
      setResumeFile(null);
    } catch {
      setResumeStatus("Failed to analyze resume");
    } finally {
      setResumeLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <div className="w-full max-w-5xl grid lg:grid-cols-2 gap-6 px-4">
      <Card className="w-full bg-gray-950 border-gray-800 text-white">
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

      <Card className="w-full bg-gray-950 border-gray-800 text-white">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-cyan-400" />
            Founder Background Analysis
          </CardTitle>
          <p className="text-sm text-gray-400">
            Optional CV enrichment. This is additive, not mandatory. If the resume is sparse, the system treats it as a weak signal and still relies on assessment answers.
          </p>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="rounded-2xl border border-gray-800 bg-black/40 p-4">
            <div className="flex items-start justify-between gap-4 mb-4">
              <div>
                <div className="text-sm font-semibold text-white mb-1">Upload Resume / CV</div>
                <p className="text-xs text-gray-500">Accepted formats: PDF or TXT. Best used to enrich founder-fit, venture-fit, and recommendations.</p>
              </div>
              <FileText className="h-5 w-5 text-cyan-400" />
            </div>
            <input
              type="file"
              accept=".pdf,.txt"
              onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-gray-400 file:mr-4 file:rounded-lg file:border-0 file:bg-cyan-500/15 file:px-3 file:py-2 file:text-sm file:font-medium file:text-cyan-300 hover:file:bg-cyan-500/20"
            />
            <div className="mt-4 flex items-center gap-3">
              <Button
                type="button"
                onClick={handleResumeUpload}
                disabled={resumeLoading || !resumeFile}
                className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 text-white"
              >
                <Upload className="h-4 w-4 mr-2" />
                {resumeLoading ? 'Analyzing...' : 'Analyze Resume'}
              </Button>
              {resumeStatus && <span className="text-sm text-gray-400">{resumeStatus}</span>}
            </div>
          </div>

          {resumeData?.inferred_profile && (
            <div className="rounded-2xl border border-gray-800 bg-black/40 p-4 space-y-3">
              <div className="text-sm font-semibold text-white">Extracted Signals</div>
              <div className="grid md:grid-cols-2 gap-3 text-sm">
                <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-3">
                  <div className="text-gray-500 text-xs mb-1">Current Role</div>
                  <div className="text-white">{resumeData.inferred_profile.current_role || 'Not detected'}</div>
                </div>
                <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-3">
                  <div className="text-gray-500 text-xs mb-1">Years Experience</div>
                  <div className="text-white">{resumeData.inferred_profile.years_experience || 0}</div>
                </div>
                <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-3 md:col-span-2">
                  <div className="text-gray-500 text-xs mb-1">Skill Clusters</div>
                  <div className="text-white">{(resumeData.inferred_profile.skill_clusters || []).join(', ') || 'No strong clusters detected'}</div>
                </div>
                <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-3 md:col-span-2">
                  <div className="text-gray-500 text-xs mb-1">Industry Signals</div>
                  <div className="text-white">{(resumeData.inferred_profile.industries || []).join(', ') || 'No clear domain specialization detected'}</div>
                </div>
              </div>
            </div>
          )}

          {resumeAnalysis && (
            <div className="rounded-2xl border border-cyan-500/20 bg-gradient-to-br from-cyan-500/6 to-purple-500/6 p-4 space-y-4">
              <div>
                <div className="text-xs uppercase tracking-wide text-cyan-400 font-semibold mb-2">Analysis Summary</div>
                <p className="text-sm text-gray-300 leading-relaxed">{resumeAnalysis.summary}</p>
              </div>

              <div>
                <div className="text-sm font-semibold text-white mb-2">Founder Strengths</div>
                <ul className="list-disc pl-5 space-y-1 text-sm text-gray-400">
                  {(resumeAnalysis.founder_strengths || []).map((item, idx) => <li key={idx}>{item}</li>)}
                </ul>
              </div>

              <div>
                <div className="text-sm font-semibold text-white mb-2">Likely Venture Fit</div>
                <ul className="list-disc pl-5 space-y-1 text-sm text-gray-400">
                  {(resumeAnalysis.venture_fit?.strongest_matches || []).map((item, idx) => <li key={idx}>{item}</li>)}
                </ul>
              </div>

              <div>
                <div className="text-sm font-semibold text-white mb-2">Potential Gaps</div>
                <ul className="list-disc pl-5 space-y-1 text-sm text-gray-400">
                  {(resumeAnalysis.possible_gaps || []).map((item, idx) => <li key={idx}>{item}</li>)}
                </ul>
              </div>

              <div>
                <div className="text-sm font-semibold text-white mb-2">Recommended Use</div>
                <ul className="list-disc pl-5 space-y-1 text-sm text-gray-400">
                  {(resumeAnalysis.recommendations || []).map((item, idx) => <li key={idx}>{item}</li>)}
                </ul>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
      </div>

      {/* Privacy & Connections row */}
      <div className="w-full max-w-5xl mx-auto px-4 grid sm:grid-cols-2 gap-4 pb-8">
        <Link to="/profile/consent" className="group">
          <Card className="bg-gray-950 border-gray-800 text-white hover:border-indigo-500 transition-colors">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="p-2 rounded-lg bg-indigo-500/10">
                <Shield className="h-5 w-5 text-indigo-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm text-white">Privacy & Consent</div>
                <div className="text-xs text-gray-400">Manage GDPR consent for each data category</div>
              </div>
              <ChevronRight className="h-4 w-4 text-gray-600 group-hover:text-indigo-400 transition-colors" />
            </CardContent>
          </Card>
        </Link>

        <Link to="/profile/connections" className="group">
          <Card className="bg-gray-950 border-gray-800 text-white hover:border-indigo-500 transition-colors">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="p-2 rounded-lg bg-emerald-500/10">
                <Link2 className="h-5 w-5 text-emerald-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm text-white">Connected Accounts</div>
                <div className="text-xs text-gray-400">Email, MicroMentor and other external accounts</div>
              </div>
              <ChevronRight className="h-4 w-4 text-gray-600 group-hover:text-emerald-400 transition-colors" />
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
};

export default ProfileSettings;
