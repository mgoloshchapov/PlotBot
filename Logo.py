import matplotlib.pyplot as plt


plt.title('With love')
plt.xlabel('AMK')
plt.ylabel('from')
plt.xticks([])
plt.yticks([])

plt.plot([7, 5, 5, 6, 7, 8, 9, 9, 7], [2, 5, 6, 7, 6, 7, 6, 5, 2], 'red')

plt.plot([6, 5.1, 6.3, 5.5, 7, 6, 7.1, 6.5, 7.5, 7.1, 8, 7.75, 8.25, 8.6, 8.5, 8.9, 8],
         [6.9, 5.5, 6.3, 4.7, 5.9, 4, 5.6, 3.2, 5.8, 2.7, 6, 3.5, 5.5, 4.75, 5.9, 5.5, 7], 'green')
plt.show()