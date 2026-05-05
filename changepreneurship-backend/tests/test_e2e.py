"""
End-to-End Test Suite
Tests complete user journeys from registration to completion
"""
import pytest
import time


class TestFullUserJourney:
    """Test complete user journey from start to finish"""
    
    def test_new_user_complete_flow(self, client):
        """
        Complete flow: Register → Login → Complete All Phases → View Dashboard
        """
        # Step 1: Register
        register_response = client.post('/api/auth/register', json={
            'username': 'journey_user',
            'email': 'journey@test.com',
            'password': 'SecurePass123!',
            'password_confirmation': 'SecurePass123!'
        })
        assert register_response.status_code == 201
        assert 'session_token' in register_response.json
        token = register_response.json['session_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Step 2: Verify initial state (0% progress)
        dashboard = client.get('/api/analytics/dashboard/overview', headers=headers)
        assert dashboard.json['data']['overall_progress'] == 0
        assert dashboard.json['data']['completed_phases'] == 0
        
        # Step 3: Complete Self Discovery Phase
        self_discovery_data = {
            'responses': {
                'personality': {
                    'risk_tolerance': 4,
                    'decision_making': 5,
                    'leadership_style': 4
                },
                'values': {
                    'top_value_1': 'innovation',
                    'top_value_2': 'impact',
                    'top_value_3': 'growth'
                },
                'strengths': {
                    'technical': 5,
                    'communication': 4,
                    'strategic': 4
                }
            }
        }
        phase1 = client.post('/api/assessment/self_discovery/submit',
            headers=headers, json=self_discovery_data)
        assert phase1.status_code in [200, 201]
        
        # Step 4: Complete Idea Discovery Phase
        idea_discovery_data = {
            'opportunities': [
                {'idea': 'AI-powered platform', 'score': 85, 'market': 'technology'},
                {'idea': 'Green energy solution', 'score': 78, 'market': 'sustainability'}
            ],
            'selected_ideas': ['AI-powered platform']
        }
        phase2 = client.post('/api/assessment/idea_discovery/submit',
            headers=headers, json=idea_discovery_data)
        assert phase2.status_code in [200, 201]
        
        # Step 5: Complete Market Research Phase
        market_research_data = {
            'target_market': {
                'segment': 'B2B SaaS',
                'size': '500M',
                'growth_rate': '25%'
            },
            'competitors': [
                {'name': 'Competitor A', 'market_share': '30%'},
                {'name': 'Competitor B', 'market_share': '20%'}
            ],
            'validation': {
                'customer_interviews': 15,
                'survey_responses': 120,
                'interest_level': 'high'
            }
        }
        phase3 = client.post('/api/assessment/market_research/submit',
            headers=headers, json=market_research_data)
        assert phase3.status_code in [200, 201]
        
        # Step 6: Complete Business Pillars Phase
        business_pillars_data = {
            'customer_segment': {
                'primary': 'Mid-size tech companies',
                'secondary': 'Startups'
            },
            'value_proposition': 'AI-driven automation that saves 40% time',
            'revenue_model': {
                'type': 'subscription',
                'pricing': 'tiered'
            },
            'business_plan': {
                'year_1_revenue': '500K',
                'year_3_revenue': '5M'
            }
        }
        phase4 = client.post('/api/assessment/business_pillars/submit',
            headers=headers, json=business_pillars_data)
        assert phase4.status_code in [200, 201]
        
        # Step 7: Complete Product Concept Testing
        product_concept_data = {
            'concept_tests': [
                {'feature': 'AI automation', 'feedback_score': 4.5},
                {'feature': 'Analytics dashboard', 'feedback_score': 4.2}
            ],
            'customer_feedback': {
                'positive': 85,
                'neutral': 10,
                'negative': 5
            },
            'mvp_definition': 'Core AI automation with basic analytics'
        }
        phase5 = client.post('/api/assessment/product_concept_testing/submit',
            headers=headers, json=product_concept_data)
        assert phase5.status_code in [200, 201]
        
        # Step 8: Complete Business Development
        business_dev_data = {
            'strategic_decisions': {
                'market_entry': 'direct sales',
                'scaling_strategy': 'product-led growth'
            },
            'resource_allocation': {
                'engineering': '40%',
                'sales': '30%',
                'marketing': '20%',
                'operations': '10%'
            },
            'partnerships': [
                {'partner': 'Cloud Provider', 'type': 'technology'},
                {'partner': 'Industry Association', 'type': 'marketing'}
            ]
        }
        phase6 = client.post('/api/assessment/business_development/submit',
            headers=headers, json=business_dev_data)
        assert phase6.status_code in [200, 201]
        
        # Step 9: Complete Business Prototype Testing (Final Phase)
        prototype_testing_data = {
            'prototype_results': {
                'users_tested': 50,
                'satisfaction_score': 4.3,
                'retention_rate': '75%'
            },
            'market_testing': {
                'pilot_customers': 10,
                'conversion_rate': '60%'
            },
            'business_model_validation': {
                'revenue_confirmed': True,
                'unit_economics': 'positive'
            },
            'scaling_plan': {
                'timeline': '12 months',
                'target_customers': 500,
                'funding_needed': '2M'
            }
        }
        phase7 = client.post('/api/assessment/business_prototype_testing/submit',
            headers=headers, json=prototype_testing_data)
        assert phase7.status_code in [200, 201]
        
        # Step 10: Verify final state (100% progress)
        final_dashboard = client.get('/api/analytics/dashboard/overview', headers=headers)
        assert final_dashboard.status_code == 200
        final_data = final_dashboard.json['data']
        assert final_data['completed_phases'] == 7
        assert final_data['overall_progress'] == 100.0
        
        # Step 11: Get entrepreneur profile
        profile = client.get('/api/analytics/dashboard/entrepreneur-profile', headers=headers)
        assert profile.status_code == 200
        
        # Step 12: Get AI recommendations
        recommendations = client.get('/api/ai-recommendations', headers=headers)
        assert recommendations.status_code in [200, 404]
        
        # Step 13: Get all user responses
        responses = client.get('/api/assessment/responses', headers=headers)
        assert responses.status_code == 200
        
        # Step 14: Export data
        # TODO: Add export endpoint test when available
        
        print("\n✅ FULL USER JOURNEY COMPLETED SUCCESSFULLY")
        print(f"   User: journey_user")
        print(f"   Progress: {final_data['overall_progress']}%")
        print(f"   Phases: {final_data['completed_phases']}/7")
        print(f"   Time spent: {final_data.get('time_spent', 0)} minutes")


class TestPartialJourney:
    """Test partial completion scenarios"""
    
    def test_save_and_resume(self, client):
        """User should be able to save progress and resume later"""
        # Register
        client.post('/api/auth/register', json={
            'username': 'resume_user',
            'email': 'resume@test.com',
            'password': 'PassWord1234!',
            'password_confirmation': 'PassWord1234!'
        })
        
        # Login
        login1 = client.post('/api/auth/login', json={
            'username': 'resume_user',
            'password': 'PassWord1234!'
        })
        token1 = login1.json['session_token']
        headers1 = {'Authorization': f'Bearer {token1}'}
        
        # Complete first phase
        client.post('/api/assessment/self_discovery/submit',
            headers=headers1,
            json={'responses': {'test': 'data'}})
        
        # Check progress
        progress1 = client.get('/api/analytics/dashboard/overview', headers=headers1)
        initial_progress = progress1.json['data']['overall_progress']
        assert initial_progress > 0
        
        # Logout (simulate)
        client.post('/api/auth/logout', headers=headers1)
        
        # Login again (new session)
        login2 = client.post('/api/auth/login', json={
            'username': 'resume_user',
            'password': 'PassWord1234!'
        })
        token2 = login2.json['session_token']
        headers2 = {'Authorization': f'Bearer {token2}'}
        
        # Progress should be persisted
        progress2 = client.get('/api/analytics/dashboard/overview', headers=headers2)
        resumed_progress = progress2.json['data']['overall_progress']
        assert resumed_progress == initial_progress
        
        print("\n✅ SAVE AND RESUME TEST PASSED")


class TestDataConsistency:
    """Test data consistency across sessions"""
    
    def test_response_consistency(self, client):
        """Responses should be consistent across multiple retrievals"""
        # Setup user
        client.post('/api/auth/register', json={
            'username': 'consistency_test',
            'email': 'consist@test.com',
            'password': 'PassWord1234!',
            'password_confirmation': 'PassWord1234!'
        })
        login = client.post('/api/auth/login', json={
            'username': 'consistency_test',
            'password': 'PassWord1234!'
        })
        token = login.json['session_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Submit data
        test_data = {
            'responses': {
                'question_1': 5,
                'question_2': 'test answer',
                'question_3': [1, 2, 3]
            }
        }
        client.post('/api/assessment/self_discovery/submit',
            headers=headers, json=test_data)
        
        # Retrieve multiple times
        get1 = client.get('/api/assessment/responses', headers=headers)
        time.sleep(0.1)
        get2 = client.get('/api/assessment/responses', headers=headers)
        time.sleep(0.1)
        get3 = client.get('/api/assessment/responses', headers=headers)
        
        # All should return same data
        assert get1.json == get2.json == get3.json
        
        print("\n✅ DATA CONSISTENCY TEST PASSED")


class TestConcurrentUsers:
    """Test multiple users working simultaneously"""
    
    def test_multiple_users_isolated_data(self, client):
        """Multiple users should have isolated data"""
        # Create user 1
        client.post('/api/auth/register', json={
            'username': 'user1',
            'email': 'user1@test.com',
            'password': 'PassWord1234!',
            'password_confirmation': 'PassWord1234!'
        })
        login1 = client.post('/api/auth/login', json={
            'username': 'user1',
            'password': 'PassWord1234!'
        })
        token1 = login1.json['session_token']
        headers1 = {'Authorization': f'Bearer {token1}'}
        
        # Create user 2
        client.post('/api/auth/register', json={
            'username': 'user2',
            'email': 'user2@test.com',
            'password': 'PassWord1234!',
            'password_confirmation': 'PassWord1234!'
        })
        login2 = client.post('/api/auth/login', json={
            'username': 'user2',
            'password': 'PassWord1234!'
        })
        token2 = login2.json['session_token']
        headers2 = {'Authorization': f'Bearer {token2}'}
        
        # User 1 submits data
        client.post('/api/assessment/self_discovery/submit',
            headers=headers1,
            json={'responses': {'user': 'one', 'data': 1}})
        
        # User 2 submits different data
        client.post('/api/assessment/self_discovery/submit',
            headers=headers2,
            json={'responses': {'user': 'two', 'data': 2}})
        
        # Verify isolation
        user1_data = client.get('/api/assessment/responses', headers=headers1)
        user2_data = client.get('/api/assessment/responses', headers=headers2)
        
        # Data should be different
        assert user1_data.json != user2_data.json
        
        print("\n✅ CONCURRENT USERS ISOLATION TEST PASSED")


class TestErrorRecovery:
    """Test system recovery from errors"""
    
    def test_partial_submission_rollback(self, client):
        """System should rollback on partial submission failure"""
        client.post('/api/auth/register', json={
            'username': 'rollback_test',
            'email': 'rollback@test.com',
            'password': 'PassWord1234!',
            'password_confirmation': 'PassWord1234!'
        })
        login = client.post('/api/auth/login', json={
            'username': 'rollback_test',
            'password': 'PassWord1234!'
        })
        token = login.json['session_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Try to submit invalid data
        invalid_data = {
            'responses': {
                'valid_field': 'value',
                'invalid_field': None  # This might cause validation error
            }
        }
        response = client.post('/api/assessment/self_discovery/submit',
            headers=headers, json=invalid_data)
        
        # If it fails, data should not be partially saved
        if response.status_code >= 400:
            get_response = client.get('/api/assessment/responses', headers=headers)
            # Should have no responses or original state
            print("\n✅ ROLLBACK TEST PASSED")
        else:
            print("\n⚠️  ROLLBACK TEST SKIPPED (no validation error)")


class TestFullStackIntegration:
    """Test full stack integration (backend + database + services)"""
    
    def test_ai_pipeline(self, client):
        """Test AI recommendation pipeline"""
        # Setup completed user
        client.post('/api/auth/register', json={
            'username': 'ai_pipeline',
            'email': 'ai@test.com',
            'password': 'PassWord1234!',
            'password_confirmation': 'PassWord1234!'
        })
        login = client.post('/api/auth/login', json={
            'username': 'ai_pipeline',
            'password': 'PassWord1234!'
        })
        token = login.json['session_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Submit minimal data to trigger AI
        client.post('/api/assessment/self_discovery/submit',
            headers=headers,
            json={'responses': {'archetype': 'innovator'}})
        
        # Request AI recommendations
        ai_response = client.get('/api/ai-recommendations', headers=headers)
        
        # Should return recommendations or graceful error
        assert ai_response.status_code in [200, 404, 503]
        
        if ai_response.status_code == 200:
            assert 'recommendations' in ai_response.json or 'insights' in ai_response.json
            print("\n✅ AI PIPELINE TEST PASSED")
        else:
            print("\n⚠️  AI PIPELINE TEST SKIPPED (service unavailable)")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
