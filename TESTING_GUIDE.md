# Testing Guide - Privacy & Statistics Features

## ✅ Implementation Status

All security and feature improvements have been successfully implemented:

- ✅ **Private Portfolio** - Requires JWT authentication + wallet connection
- ✅ **Statistics Modal** - Beautiful chart visualization with Chart.js
- ✅ **Backend Authentication** - Portfolio endpoint now validates user ownership
- ✅ **Error Handling** - Clear messages for unauthorized access
- ✅ **Responsive Design** - Works on all devices

---

## 🧪 Testing Scenarios

### Test 1: Portfolio Privacy - Unauthorized Access

**Objective:** Verify portfolio is hidden without login

**Steps:**
1. Open http://localhost:8000 in browser
2. Scroll to "My Portfolio" section
3. Observe: Shows "Connect wallet to view portfolio"
4. Conclusion: ✅ Portfolio is hidden

---

### Test 2: Portfolio Privacy - Login Required

**Objective:** Verify login is required to see portfolio

**Steps:**
1. Click "Login" button (top right)
2. Enter your registered email and password
3. Click "Login"
4. Scroll to "My Portfolio" section
5. Observe: Still shows "Please connect your wallet to view your portfolio"
6. Conclusion: ✅ Login alone is not enough

---

### Test 3: Portfolio Privacy - Wallet Connection Required

**Objective:** Verify wallet connection is required

**Steps:**
1. (After logging in) Click "Connect Wallet" button
2. If wallet.js is configured, wallet connects
3. Scroll to "My Portfolio" section
4. Observe: Now shows your investments (or "No investments yet" if none)
5. Conclusion: ✅ Both login AND wallet required

---

### Test 4: Private Data Isolation

**Objective:** Verify users only see their own investments

**Steps:**
1. User A: Login and connect wallet
2. User A: Note their portfolio contents (or empty)
3. User A: Make an investment (or skip if no bond selected)
4. User A: Verify investment appears in portfolio
5. User A: Logout
6. User B: Login with different account and connect wallet B
7. User B: Check portfolio - should NOT see User A's investments
8. Conclusion: ✅ Data is isolated by user

---

### Test 5: Statistics Modal - Display

**Objective:** Verify statistics modal works

**Steps:**
1. Scroll to "Platform Statistics" section
2. Click "📊 View Detailed Stats" button
3. Observe: Modal opens with:
   - Title: "📊 Platform Statistics"
   - 4 gradient stat cards (colorful)
   - Doughnut chart showing data distribution
4. Click X button to close
5. Conclusion: ✅ Modal displays correctly

---

### Test 6: Statistics Chart - Data Display

**Objective:** Verify chart displays correct data

**Steps:**
1. Click "📊 View Detailed Stats" button
2. Check chart legend shows: "Total Investors", "Bond Types", "Active Investments"
3. Check colored segments match the legend
4. Verify numbers match the stat cards above chart
5. Conclusion: ✅ Chart data is accurate

---

### Test 7: API Security - Unauthorized Portfolio Access

**Objective:** Verify API rejects unauthorized requests

**Steps:**
1. Open browser developer tools (F12)
2. Go to Console tab
3. Paste:
```javascript
fetch('http://localhost:8000/api/portfolio/0x123')
  .then(r => r.json())
  .then(d => console.log('Status:', r.status, 'Data:', d))
```
4. Observe: Returns 401 Unauthorized or similar error
5. Conclusion: ✅ API is protected

---

### Test 8: API Security - Valid Token Access

**Objective:** Verify API allows authorized requests

**Steps:**
1. Open browser developer tools (F12)
2. Go to Console tab
3. Paste:
```javascript
// Get your current auth token
const token = localStorage.getItem('authToken');
console.log('Token:', token ? 'exists' : 'missing');

// Try portfolio with token
const address = '0x123'; // Use your actual wallet address
fetch(`http://localhost:8000/api/portfolio/${address}`, {
  headers: { 'Authorization': `Bearer ${token}` }
})
  .then(r => r.json())
  .then(d => console.log('Portfolio:', d))
```
4. Observe: Returns your portfolio data
5. Conclusion: ✅ API works with valid token

---

### Test 9: Responsive Design - Mobile

**Objective:** Verify all features work on mobile

**Steps:**
1. Open http://localhost:8000 in browser
2. Press F12 to open developer tools
3. Click device toggle (mobile icon) to enable mobile view
4. Test all features:
   - Portfolio loading
   - Statistics modal opening
   - Chart display
   - Form inputs
5. Conclusion: ✅ Mobile responsive

---

### Test 10: Error States - Expired Session

**Objective:** Verify error handling for expired tokens

**Steps:**
1. Login normally
2. Open browser developer tools Console
3. Clear the auth token:
```javascript
localStorage.removeItem('authToken');
```
4. Try to refresh portfolio:
```javascript
// Go to portfolio section and check console
```
5. Observe: Shows error message "Unauthorized: Invalid or expired session"
6. Conclusion: ✅ Error handling works

---

## 📊 Feature Verification Checklist

### Portfolio Privacy
- [ ] Portfolio hidden without login
- [ ] Portfolio hidden without wallet connection
- [ ] Portfolio visible with both login + wallet
- [ ] Users only see their own investments
- [ ] Error messages are clear and helpful
- [ ] API returns 403 for unauthorized access
- [ ] API returns 401 for missing authentication

### Statistics Modal
- [ ] "View Detailed Stats" button visible
- [ ] Modal opens when button clicked
- [ ] Modal closes when X clicked
- [ ] Modal closes when clicking outside
- [ ] Stat cards display all 4 metrics
- [ ] Chart displays doughnut visualization
- [ ] Chart has legend with all items
- [ ] Numbers match stat cards

### Error Handling
- [ ] "Please log in..." message shows correctly
- [ ] "Please connect wallet..." message shows correctly
- [ ] "Unauthorized" message shows when needed
- [ ] Error messages styled in red
- [ ] No JavaScript errors in console

### Security
- [ ] Token sent in Authorization header
- [ ] API validates token on portfolio endpoint
- [ ] API checks user owns portfolio
- [ ] Cannot access other users' portfolios
- [ ] Graceful error for invalid tokens

### UI/UX
- [ ] Modal responsive on mobile
- [ ] Chart responsive on mobile
- [ ] All buttons clickable and functional
- [ ] Loading overlay works
- [ ] No layout issues or overflow

---

## 🔍 Console Testing Commands

### Check Current Auth Status
```javascript
console.log('Token:', localStorage.getItem('authToken'));
console.log('User:', localStorage.getItem('user'));
```

### Load Statistics
```javascript
fetch('http://localhost:8000/api/investments/stats')
  .then(r => r.json())
  .then(d => console.log('Stats:', d))
```

### List Available Bonds
```javascript
fetch('http://localhost:8000/api/bonds')
  .then(r => r.json())
  .then(d => console.log('Bonds:', d))
```

### Check Portfolio (Requires Auth)
```javascript
const token = localStorage.getItem('authToken');
fetch('http://localhost:8000/api/portfolio/YOUR_ADDRESS_HERE', {
  headers: { 'Authorization': `Bearer ${token}` }
})
  .then(r => r.json())
  .then(d => console.log('Portfolio:', d))
```

---

## 📱 Mobile Testing

### Device Testing Checklist
- [ ] iPhone 12
- [ ] iPad
- [ ] Android Phone
- [ ] Tablet

### Responsive Breakpoints Tested
- [ ] 480px (Mobile)
- [ ] 768px (Tablet)
- [ ] 1024px (Desktop)
- [ ] 1200px+ (Large Desktop)

---

## 🚨 Expected Error Messages

### When Not Logged In
```
"Please log in to view your portfolio"
```

### When Wallet Not Connected
```
"Please connect your wallet to view your portfolio"
```

### When Token Expired/Invalid
```
"Unauthorized: Invalid or expired session"
```

### When Accessing Another's Portfolio
```
"403 Forbidden - You can only access your own portfolio"
```

---

## 📝 Test Results Template

```
Test Date: _______________
Tester: ___________________

Portfolio Privacy:     [ ] Pass  [ ] Fail
Statistics Modal:      [ ] Pass  [ ] Fail
Chart Display:         [ ] Pass  [ ] Fail
API Security:          [ ] Pass  [ ] Fail
Error Handling:        [ ] Pass  [ ] Fail
Responsive Design:     [ ] Pass  [ ] Fail
Overall Status:        [ ] Pass  [ ] Fail

Issues Found:
_________________________________
_________________________________
_________________________________

Notes:
_________________________________
_________________________________
_________________________________
```

---

## ✅ Sign-Off Checklist

Before considering this feature complete:

- [ ] All 10 test scenarios completed
- [ ] No errors in browser console
- [ ] Backend server running smoothly
- [ ] No security warnings
- [ ] Mobile testing passed
- [ ] Error messages working
- [ ] Chart displaying correctly
- [ ] Portfolio data isolation verified
- [ ] User authenticated properly
- [ ] Ready for production

---

## 🔧 Troubleshooting

### Issue: Portfolio shows "Connect wallet" even when logged in
**Solution:** Ensure wallet.js is loaded and walletManager is available

### Issue: Chart not displaying
**Solution:** Check Chart.js library loaded, open DevTools Console for errors

### Issue: Statistics modal won't open
**Solution:** Check HTML has `id="statsModal"` and `id="statsModalBtn"`

### Issue: "Bearer" authentication not working
**Solution:** Ensure authToken is stored in localStorage after login

### Issue: API returns 403 instead of showing portfolio
**Solution:** Verify wallet address matches the one in database, check user owns that wallet

---

**All tests should PASS before deploying to production.**
